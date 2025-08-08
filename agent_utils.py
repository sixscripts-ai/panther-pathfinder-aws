"""
Agent utilities for Panther Pathfinder
Contains functions to add agent capabilities to the existing chatbot
"""

import boto3
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import re

def create_agent_tools(bedrock_client) -> Dict[str, Callable]:
    """Create a dictionary of tools that an agent can use"""
    
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base for information"""
        try:
            response = bedrock_client.retrieve_and_generate(
                input={'text': query},
                retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': '''You are a question answering agent designed to help the user get to one location to another. The user will provide you with their location and a question. Your job is to answer the user's question using only information from the database as concisely as possible. If the results do not contain information that can answer the question, please state that you could not find an exact answer to the question.

                                                    When retrieving information about meeting locations, only answer based on hartnell/expanded_courses_all.html.

                                                    When asked how to go from one place to another, give detailed instructions and refer to neighboring landmarks to help the user go to the destination.

                                                    If the user does not specify the year and semester, prompt the user if clarification is needed. If the user mentions multiple classes, pick the semester in which they all occur.

                                                    Here are the search results in numbered order:
                                                    $search_results$

                                                    $output_format_instructions$'''
                        }
                    },
                    'knowledgeBaseId': 'Y4NJOU25DB' ,
                    'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
                },
                'type': 'KNOWLEDGE_BASE'
            }
        )
            if response and 'output' in response:
                return response['output']['text']
            return "No information found in knowledge base."
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    def get_current_time() -> str:
        """Get the current date and time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def calculate_math(expression: str) -> str:
        """Safely evaluate mathematical expressions"""
        try:
            # Only allow basic math operations for security
            allowed_chars = set('0123456789+-*/.() ')
            clean_expr = ''.join(c for c in expression if c in allowed_chars)
            if clean_expr and len(clean_expr) > 0:
                result = eval(clean_expr)
                return f"Result: {result}"
            else:
                return "Invalid expression - only basic math operations allowed"
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
    
    def analyze_text(text: str) -> str:
        """Analyze text for sentiment, length, etc."""
        word_count = len(text.split())
        char_count = len(text)
        return f"Text analysis - Words: {word_count}, Characters: {char_count}"
    
    return {
        "search_knowledge_base": search_knowledge_base,
        "get_current_time": get_current_time,
        "calculate_math": calculate_math,
        "analyze_text": analyze_text
    }

def process_with_agent(user_input: str, tools: Dict[str, Callable], bedrock_runtime_client) -> str:
    """
    Process user input with agent capabilities
    The agent can decide which tools to use based on the input
    """
    
    # Create tool descriptions for the agent
    tool_descriptions = {
        "search_knowledge_base": "Search internal knowledge base for specific information",
        "get_current_time": "Get current date and time",
        "calculate_math": "Perform mathematical calculations",
        "analyze_text": "Analyze text for word count, character count, etc."
    }
    
    # Create agent prompt
    agent_prompt = f"""You are an intelligent assistant with access to these tools:

{json.dumps(tool_descriptions, indent=2)}

User query: "{user_input}"

You are a question answering agent designed to help the user get to one location to another. The user will provide you with their location and a question. Your job is to answer the user's question using only information from the database as concisely as possible. If the results do not contain information that can answer the question, please state that you could not find an exact answer to the question.

                                                    When asked how to go from one place to another, give detailed instructions and refer to neighboring landmarks to help the user go to the destination.

                                                    If the user does not specify the year and semester, prompt the user if clarification is needed. If the user mentions multiple classes, pick the semester in which they all occur.

                                                    Here are the search results in numbered order:
                                                    $search_results$

                                                    $output_format_instructions$"""

    try:
        # Get agent decision from Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": agent_prompt}]
        })
        
        response = bedrock_runtime_client.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        agent_thinking = response_body['content'][0]['text']
        
        # Execute tools based on analysis
        tool_results = []
        
        # Check for knowledge base search need
        kb_keywords = ['company', 'product', 'service', 'policy', 'procedure', 'information', 'what is', 'how to', 'explain']
        if any(keyword in user_input.lower() for keyword in kb_keywords):
            kb_result = tools["search_knowledge_base"](user_input)
            tool_results.append(f"🔍 **Knowledge Base Search:**\n{kb_result}")
        
        # Check for time request
        time_keywords = ['time', 'date', 'when', 'current']
        if any(keyword in user_input.lower() for keyword in time_keywords):
            time_result = tools["get_current_time"]()
            tool_results.append(f"🕒 **Current Time:** {time_result}")
        
        # Check for math calculation
        math_patterns = [r'\d+\s*[+\-*/]\s*\d+', r'calculate', r'math', r'compute']
        if any(re.search(pattern, user_input.lower()) for pattern in math_patterns):
            # Extract numbers and operators
            math_expr = re.findall(r'[\d+\-*/().\s]+', user_input)
            if math_expr:
                math_result = tools["calculate_math"](''.join(math_expr))
                tool_results.append(f"🧮 **Calculation:** {math_result}")
        
        # Check for text analysis
        if 'analyze' in user_input.lower() or 'count' in user_input.lower():
            # Find text to analyze (simple heuristic)
            text_to_analyze = user_input
            if 'analyze' in user_input.lower():
                parts = user_input.lower().split('analyze')
                if len(parts) > 1:
                    text_to_analyze = parts[1].strip(' "\'')
            
            analysis_result = tools["analyze_text"](text_to_analyze)
            tool_results.append(f"📊 **Text Analysis:** {analysis_result}")
        
        # Combine results
        if tool_results:
            tool_output = "\n\n".join(tool_results)
            
            # Create final response using the tool results
            final_prompt = f"""Based on the user query: "{user_input}"

I used these tools and got these results:
{tool_output}

Please provide a helpful, comprehensive response that incorporates these tool results naturally."""
            
            final_body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": final_prompt}]
            })
            
            final_response = bedrock_runtime_client.invoke_model(
                modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                body=final_body
            )
            
            final_response_body = json.loads(final_response['body'].read())
            final_answer = final_response_body['content'][0]['text']
            
            # return f"{final_answer}\n\n---\n**Tool Usage:**\n{tool_output}"
            return f"\n{tool_output}"
      
        else:
            # No tools needed, just return agent thinking
            return agent_thinking
            
    except Exception as e:
        return f"Error in agent processing: {str(e)}"

def add_agent_to_existing_app():
    """
    Instructions for adding agent capabilities to the existing app
    """
    instructions = """
    To add agent capabilities to your existing app.py:
    
    1. Import agent_utils at the top:
       from agent_utils import create_agent_tools, process_with_agent
    
    2. Add bedrock runtime client:
       bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    3. In initialize_session(), add:
       if "agent_tools" not in st.session_state:
           st.session_state.agent_tools = create_agent_tools(bedrock_client)
    
    4. In the sidebar, add an agent mode toggle:
       use_agent = st.checkbox("🤖 Enable Agent Mode", value=True)
    
    5. In the chat response section, modify to:
       if use_agent:
           response_text = process_with_agent(user_input, st.session_state.agent_tools, bedrock_runtime)
           st.markdown(response_text)
           # Add to messages...
       else:
           # Your existing knowledge base query code
    """
    return instructions
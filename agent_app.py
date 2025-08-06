import streamlit as st
import boto3
import json
from typing import Dict, List, Any, Optional, Callable
import time
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Panther Pathfinder - AI Agent Assistant",
    page_icon="🐾",
    layout="wide"
)

# Bedrock clients
bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

# Agent configuration
AGENT_ID = "your-agent-id-here"  # Replace with your actual Bedrock Agent ID
AGENT_ALIAS_ID = "TSTALIASID"    # Or your specific alias ID

def invoke_bedrock_agent(agent_id: str, agent_alias_id: str, session_id: str, input_text: str) -> Dict[str, Any]:
    """Invoke a Bedrock Agent"""
    try:
        response = bedrock_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text
        )
        
        # Process the streaming response
        result = {"completion": "", "citations": [], "trace": []}
        
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result["completion"] += chunk['bytes'].decode('utf-8')
            elif 'trace' in event:
                result["trace"].append(event['trace'])
                
        return result
    except Exception as e:
        st.error(f"Error invoking agent: {str(e)}")
        return None

def query_knowledge_base_direct(query: str) -> Optional[Dict[str, Any]]:
    """Direct knowledge base query (fallback if no agent)"""
    try:
        response = bedrock_client.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': "Y4NJOU25DB",
                    'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0',
                },
                'type': 'KNOWLEDGE_BASE'
            }
        )
        return response
    except Exception as e:
        st.error(f"Error querying knowledge base: {str(e)}")
        return None

def create_custom_agent_tools() -> Dict[str, Callable]:
    """Define custom tools/functions that the agent can use"""
    
    def search_knowledge_base(query: str) -> str:
        """Search the knowledge base for information"""
        response = query_knowledge_base_direct(query)
        if response and 'output' in response:
            return response['output']['text']
        return "No information found in knowledge base."
    
    def get_current_time() -> str:
        """Get the current date and time"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def calculate_math(expression: str) -> str:
        """Safely evaluate mathematical expressions"""
        try:
            # Only allow basic math operations for security
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"Result: {result}"
            else:
                return "Invalid expression - only basic math operations allowed"
        except:
            return "Error evaluating expression"
    
    def search_web_info(query: str) -> str:
        """Placeholder for web search functionality"""
        return f"Web search functionality not implemented yet. Query was: {query}"
    
    return {
        "search_knowledge_base": search_knowledge_base,
        "get_current_time": get_current_time,
        "calculate_math": calculate_math,
        "search_web_info": search_web_info
    }

def process_with_custom_agent(user_input: str, tools: Dict[str, Callable]) -> str:
    """Simple agent pattern that can decide which tools to use"""
    
    # Create a prompt that helps the model decide which tools to use
    tool_descriptions = {
        "search_knowledge_base": "Search internal knowledge base for company/domain specific information",
        "get_current_time": "Get current date and time",
        "calculate_math": "Perform mathematical calculations",
        "search_web_info": "Search for general web information (placeholder)"
    }
    
    agent_prompt = f"""You are an intelligent assistant with access to the following tools:

{json.dumps(tool_descriptions, indent=2)}

User query: {user_input}

Based on the user's query, determine which tools to use and provide a helpful response. 

If you need to search for specific information, use search_knowledge_base.
If you need current time, use get_current_time.
If you need to do math, use calculate_math.

Think step by step about what tools you need, then provide a comprehensive answer.

Available tools: {list(tools.keys())}

Please respond with your analysis and final answer."""

    try:
        # Call Claude directly with the agent prompt
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": agent_prompt}]
        })
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        agent_response = response_body['content'][0]['text']
        
        # Simple tool detection and execution
        executed_tools = []
        
        # Check if agent wants to use knowledge base
        if "search_knowledge_base" in agent_response.lower() or "knowledge base" in user_input.lower():
            kb_result = tools["search_knowledge_base"](user_input)
            executed_tools.append(f"🔍 Knowledge Base Search: {kb_result[:200]}...")
        
        # Check if agent wants current time
        if "time" in user_input.lower() or "date" in user_input.lower():
            time_result = tools["get_current_time"]()
            executed_tools.append(f"🕒 Current Time: {time_result}")
        
        # Check for math expressions
        if any(op in user_input for op in ['+', '-', '*', '/', 'calculate', 'math']):
            # Extract potential math expression (simplified)
            import re
            math_match = re.search(r'[\d+\-*/().\s]+', user_input)
            if math_match:
                math_result = tools["calculate_math"](math_match.group())
                executed_tools.append(f"🧮 Math Result: {math_result}")
        
        # Combine results
        if executed_tools:
            tool_results = "\n\n".join(executed_tools)
            final_response = f"{agent_response}\n\n**Tool Executions:**\n{tool_results}"
        else:
            final_response = agent_response
            
        return final_response
        
    except Exception as e:
        return f"Error in custom agent processing: {str(e)}"

def display_sources(citations: List[Dict]) -> None:
    """Display source citations in an expandable section"""
    if not citations:
        return
        
    with st.expander("📚 Sources", expanded=False):
        for i, citation in enumerate(citations):
            st.write(f"**Source {i+1}:**")
            
            if 'retrievedReferences' in citation:
                for ref in citation['retrievedReferences']:
                    if 'content' in ref and 'text' in ref['content']:
                        st.write(f"Content: {ref['content']['text'][:200]}...")
                    
                    if 'location' in ref and 's3Location' in ref['location']:
                        st.write(f"Document: {ref['location']['s3Location']['uri']}")
            
            st.write("---")

def display_agent_trace(trace_data: List[Dict]) -> None:
    """Display agent reasoning trace"""
    if not trace_data:
        return
        
    with st.expander("🧠 Agent Reasoning", expanded=False):
        for i, trace in enumerate(trace_data):
            st.write(f"**Step {i+1}:**")
            st.json(trace)

def initialize_session():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"
    if "agent_tools" not in st.session_state:
        st.session_state.agent_tools = create_custom_agent_tools()

def display_chat_history():
    """Display the chat message history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant":
                if "citations" in message:
                    display_sources(message["citations"])
                if "trace" in message:
                    display_agent_trace(message["trace"])

def main():
    """Main application function"""
    
    # Page header
    st.title("🐾 Panther Pathfinder Agent")
    st.subheader("AI Agent with Knowledge Base & Tools")
    
    # Initialize session
    initialize_session()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🤖 Agent Settings")
        
        # Agent mode selection
        agent_mode = st.selectbox(
            "Agent Mode",
            ["Custom Agent (Tools)", "Direct Knowledge Base", "Bedrock Agent (if configured)"],
            index=0
        )
        
        st.markdown("**Available Tools:**")
        for tool_name, tool_func in st.session_state.agent_tools.items():
            st.write(f"• {tool_name.replace('_', ' ').title()}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Session info
        st.markdown("---")
        st.markdown("**Session Info:**")
        st.write(f"Session ID: {st.session_state.session_id}")
        st.write(f"Mode: {agent_mode}")
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if user_input := st.chat_input("Ask the agent anything..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking and using tools..."):
                
                if agent_mode == "Custom Agent (Tools)":
                    # Use custom agent with tools
                    response_text = process_with_custom_agent(user_input, st.session_state.agent_tools)
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })
                    
                elif agent_mode == "Bedrock Agent (if configured)":
                    # Use Bedrock Agent (requires agent setup)
                    agent_response = invoke_bedrock_agent(
                        AGENT_ID, 
                        AGENT_ALIAS_ID, 
                        st.session_state.session_id, 
                        user_input
                    )
                    
                    if agent_response:
                        response_text = agent_response["completion"]
                        st.markdown(response_text)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "trace": agent_response.get("trace", [])
                        })
                        
                        # Display trace
                        if agent_response.get("trace"):
                            display_agent_trace(agent_response["trace"])
                    else:
                        error_msg = "Agent invocation failed"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                
                else:
                    # Direct knowledge base query
                    response = query_knowledge_base_direct(user_input)
                    
                    if response and 'output' in response:
                        response_text = response['output']['text']
                        citations = response.get('citations', [])
                        
                        st.markdown(response_text)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "citations": citations
                        })
                        
                        if citations:
                            display_sources(citations)
                    else:
                        error_msg = "No response generated"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })

if __name__ == "__main__":
    main()
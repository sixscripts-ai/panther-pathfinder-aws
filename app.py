import streamlit as st
import boto3
import json
from typing import Dict, List, Any, Optional
from agent_utils import create_agent_tools, process_with_agent
import xml.etree.ElementTree as ET
from google_maps import get_building_directions_link
import urllib.parse

# Configure Streamlit page
st.set_page_config(
    page_title="Panther Pathfinder - AI Knowledge Assistant",
    page_icon="🐾",
    layout="wide"
)

# Bedrock clients
bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

def query_knowledge_base(client, query: str) -> Optional[Dict[str, Any]]:
    """Query the knowledge base using retrieve_and_generate"""
    # if not client:
    #     return None
        
    # knowledge_base_id = AWS_CONFIG.get('knowledge_base_id')
    # model_id = AWS_CONFIG.get('model_id', 'anthropic.claude-3-sonnet-20240229-v1:0')
    
    # if not knowledge_base_id:
    #     st.error("Knowledge Base ID not configured")
    #     return None
    
    try:
        response = bedrock_client.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'knowledgeBaseConfiguration': {
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': '''You are a question answering agent designed to help the user get to one location to another. The user will provide you with their location and a question. Your job is to answer the user's question using only information from the database as concisely as possible. If the results do not contain information that can answer the question, please state that you could not find an exact answer to the question.

                                                    When asked how to go from one place to another, give detailed instructions and refer to neighboring landmarks to help the user go to the destination.

                                                    If the user does not specify the year and semester, prompt the user if clarification is needed. If the user mentions multiple classes, pick the semester in which they all occur.

                                                    Here are the search results in numbered order:
                                                    $search_results$

                                                   respond only in the following XML format and do not include any other text:
                                                    <response>
                                                    <directions>[your natural language directions to the user]</directions>
                                                    <bldg_code>[Building code as a single uppercase letter or code]</bldg_code>
                                                    </response>'''
                        }
                    },
                    'knowledgeBaseId': 'Y4NJOU25DB' ,
                    'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0',
                },
                'type': 'KNOWLEDGE_BASE'
            }
        )
        # print(response['output']['text'])
        xml_string = response['output']['text']
        root = ET.fromstring(xml_string)
        directions = root.find("directions").text
        bldg_code = root.find("bldg_code").text
        print(bldg_code)

        bldg_link = get_building_directions_link(bldg_code)
        print(bldg_link)

        frontend_output = f"{directions} \n\nDirections to building {bldg_code}: {bldg_link}"

        return {"output": {"text": frontend_output}}
    except Exception as e:
        st.error(f"Error querying knowledge base: {str(e)}")
        return None

def display_sources(citations: List[Dict]) -> None:
    """Display source citations in an expandable section"""
    if not citations:
        return
        
    with st.expander("📚 Sources", expanded=False):
        for i, citation in enumerate(citations):
            st.write(f"**Source {i+1}:**")
            
            # Display retrieved text
            if 'retrievedReferences' in citation:
                for ref in citation['retrievedReferences']:
                    if 'content' in ref and 'text' in ref['content']:
                        st.write(f"Content: {ref['content']['text'][:200]}...")
                    
                    if 'location' in ref and 's3Location' in ref['location']:
                        st.write(f"Document: {ref['location']['s3Location']['uri']}")
            
            st.write("---")

def initialize_session():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_tools" not in st.session_state:
        st.session_state.agent_tools = create_agent_tools(bedrock_client)

def display_chat_history():
    """Display the chat message history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources for assistant messages
            if message["role"] == "assistant" and "citations" in message:
                display_sources(message["citations"])

def main():
    """Main application function"""
    
    # Page header
    st.title("🐾 Panther Pathfinder")
    st.subheader("AI-Powered Knowledge Assistant")
    
    # Initialize session
    initialize_session()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Agent mode toggle
        use_agent = st.checkbox("🤖 Enable Agent Mode", value=True, help="Agent can use multiple tools like search, calculations, etc.")
        
        if use_agent:
            st.markdown("**Available Tools:**")
            st.write("• Knowledge Base Search")
            st.write("• Current Time")
            st.write("• Math Calculator")
            st.write("• Text Analysis")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Configuration info
        st.markdown("---")
        st.markdown("**Current Settings:**")
        st.write(f"Mode: {'Agent' if use_agent else 'Knowledge Base Only'}")
    
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if user_input := st.chat_input("Ask me anything about your knowledge base..."):
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
            if use_agent:
                with st.spinner("Agent is thinking and using tools..."):
                    # Use agent with tools
                    response_text = process_with_agent(
                        user_input, 
                        st.session_state.agent_tools, 
                        bedrock_runtime
                    )
                    
                    # Display the response
                    st.markdown(response_text)
                    
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })
            else:
                with st.spinner("Searching knowledge base..."):
                    # Direct knowledge base query
                    response = query_knowledge_base(
                        bedrock_client, 
                        user_input
                    )
                    
                    if response and 'output' in response and 'text' in response['output']:
                        # Extract the generated text
                        answer = response['output']['text']
                        
                        # Display the response
                        st.markdown(answer)
                        
                        # Get citations if available
                        citations = response.get('citations', [])
                        
                        # Add to message history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "citations": citations
                        })
                        
                        # Display sources
                        if citations:
                            display_sources(citations)
                    
                    else:
                        error_msg = "I couldn't generate a response. Please try rephrasing your question."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })

if __name__ == "__main__":
    main()
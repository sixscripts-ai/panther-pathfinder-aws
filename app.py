import streamlit as st
import boto3
import json
from typing import Dict, List, Any, Optional

# Configure Streamlit page
st.set_page_config(
    page_title="Panther Pathfinder - AI Knowledge Assistant",
    page_icon="🐾",
    layout="wide"
)

# Bedrock client
bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')

def query_knowledge_base(client, query: str) -> Optional[Dict[str, Any]]:
    """Query the knowledge base using retrieve_and_generate"""
    try:
        response = bedrock_client.retrieve_and_generate(
            input={
                'text': query
            },
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
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Configuration info
        st.markdown("---")
        st.markdown("**Current Settings:**")
        st.write("Region: us-west-2")
        st.write("Model: Claude 3.5 Sonnet")
        st.write("Knowledge Base ID: Y4NJOU25DB")
    
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
            with st.spinner("Searching knowledge base..."):
                
                # Query the knowledge base
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
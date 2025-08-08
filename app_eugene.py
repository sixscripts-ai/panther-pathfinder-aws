import streamlit as st
import boto3
import json
import os
import base64
from typing import Dict, List, Any, Optional

def get_background_image_base64():
    """Convert background image to base64 for CSS"""
    background_path = "images/background.jpg"  # You can change this to your background image
    if os.path.exists(background_path):
        with open(background_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string
    return None

# Configure Streamlit page
st.set_page_config(
    page_title="Panther Pathfinder - AI Knowledge Assistant",
    page_icon="🐾",
    layout="wide"
)

# Custom CSS for background image
background_image = get_background_image_base64()

    # Fallback to dark theme if no background image
st.markdown("""
<style>
    .stApp {
        background-color: #0f1116;
    }
    
    .main {
        background-color: #0f1116;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # Page header with text at upper left
    st.markdown('<h1 style="font-weight: bold; font-size: 2.5rem;">Panther Finder</h1>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Knowledge Assistant*")
    
    # Initialize session
    initialize_session()
    
    # Centered image and text above chat box
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Display image centered using st.container with offset
        image_path = "images/panther_icon.png"
        if os.path.exists(image_path):
            with st.container():
                col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
                with col_img2:
                    st.markdown('<div style="margin-right: 10px;">', unsafe_allow_html=True)
                    st.image(image_path, width=150)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            with st.container():
                col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
                with col_img2:
                    st.markdown('<div style="margin-left: 10px;">🐾</div>', unsafe_allow_html=True)  # Fallback emoji
        
        # Text below image, centered relative to image position
        st.markdown('<div style="margin-left: 28px;"><h2 style="color: white;">Where are we going today?</h2></div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        image_path = "images/panther_icon2.png"
        
        st.markdown('<div style="margin-right: 10px;">', unsafe_allow_html=True)
        st.image(image_path, width=50)
        st.markdown('</div>', unsafe_allow_html=True)
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
    if user_input := st.chat_input("Where do you want to go today?"):
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

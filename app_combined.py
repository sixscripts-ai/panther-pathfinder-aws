import streamlit as st
import boto3
import json
import os
import base64
from typing import Dict, List, Any, Optional
from agent_utils import create_agent_tools, process_with_agent
import xml.etree.ElementTree as ET
from google_maps import get_building_directions_link, get_building_directions_link_by_name
import urllib.parse

def get_background_image_base64():
    """Convert background image to base64 for CSS"""
    background_path = "images/background.jpg"  # You can change this to your background image
    if os.path.exists(background_path):
        with open(background_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string
    return None

def get_image_base64(image_path):
    """Convert any image to base64 for embedding in HTML"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
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
    :root {
        --sidebar-width: 21rem;
    }
    
    .stApp {
        background: 
            radial-gradient(circle at top left, rgba(139, 0, 0, 0.6) 0%, transparent 40%),
            radial-gradient(circle at top right, rgba(139, 0, 0, 0.6) 0%, transparent 40%),
            #0f1116;
    }
    
    .main {
        background-color: transparent;
        color: white;
    }
    
    /* Additional styling for better visual effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at top left, rgba(100, 0, 0, 0.5) 0%, transparent 45%),
            radial-gradient(circle at top right, rgba(100, 0, 0, 0.5) 0%, transparent 45%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Make header area transparent */
    .block-container {
        background-color: transparent !important;
        padding-top: 2rem;
    }
    
    /* Make chat input area transparent */
    .stChatInput {
        background-color: transparent !important;
    }
    
    .stChatInput > div {
        background-color: rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(15px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Make the input field itself more transparent */
    .stChatInput input {
        background-color: transparent !important;
        color: white !important;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Style the chat input container */
    .stChatInput > div > div {
        background-color: transparent !important;
    }
    
    /* Remove all background from chat input elements */
    .stChatInput, .stChatInput * {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Specifically target the outer chat input wrapper */
    .stChatInput > div {
        background: rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(15px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Remove the bottom toolbar background */
    .stBottomContainer {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Target the specific chat input wrapper that might have a black background */
    div[data-testid="stChatInput"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* Make the main content area transparent */
    .main .block-container {
        background-color: transparent !important;
    }
    
    /* Ensure text visibility on transparent backgrounds */
    .stMarkdown {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# Bedrock clients
bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

def query_knowledge_base(client, query: str) -> Optional[Dict[str, Any]]:
    """Query the knowledge base using retrieve_and_generate"""
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

                                                    If the user asks about several classes, query the knowledge base for each class separately.

                                                    Here are the search results in numbered order:
                                                    $search_results$

                                                   respond only in the following XML format and do not include any other text:
                                                    <response>
                                                    <directions>[your natural language directions to the user.]</directions>
                                                    <origin_code>[Origin location code as a single uppercase letter or code]</origin_code>
                                                    <bldg_code>[Destination building code as a single uppercase letter or code]</bldg_code>
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
        
        directions_elem = root.find("directions")
        origin_code_elem = root.find("origin_code")
        bldg_code_elem = root.find("bldg_code")
        
        directions = directions_elem.text if directions_elem is not None and directions_elem.text else ""
        origin_code = origin_code_elem.text if origin_code_elem is not None and origin_code_elem.text else ""
        bldg_code = bldg_code_elem.text if bldg_code_elem is not None and bldg_code_elem.text else ""
        
        print(bldg_code)

        bldg_link = get_building_directions_link(bldg_code, origin_code, "walking")
        bldg_link2 = get_building_directions_link_by_name(bldg_code, origin_code, "walking")
        print(bldg_link)

        frontend_output = f"{directions} \n\nDirections: {bldg_link}"

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
    
    # Page header with text at upper left (from app_eugene.py)
    st.markdown('<h1 style="font-weight: bold; font-size: 2.5rem;">Panther Finder</h1>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Knowledge Assistant*")
    
    # Initialize session
    initialize_session()
    
    # Centered image and text above chat box (from app_eugene.py)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Display image centered using st.container with offset
        image_path = "images/combined_logo.png"
        if os.path.exists(image_path):
            # Simple centered image without viewport overflow
            st.markdown("""
            <div style="
                display: flex; 
                justify-content: center; 
                align-items: center; 
                width: 100%;
                padding: 0;
                margin: 0;
            ">
                <img src="data:image/png;base64,{}" width="600" style="max-width: 100%; height: auto;">
            </div>
            """.format(get_image_base64(image_path)), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                display: flex; 
                justify-content: center; 
                align-items: center;
                width: 100%;
                padding: 0;
                margin: 0;
            ">
                <div style="font-size: 4rem;">🐾</div>
            </div>
            """, unsafe_allow_html=True)  # Fallback emoji
        
        # Text below image, centered relative to image position
        # st.markdown('<div style="margin-left: 28px;"><h2 style="color: white;">Where are we going today?</h2></div>', unsafe_allow_html=True)
    
    # Sidebar for configuration (enhanced from app_eugene.py)
    with st.sidebar:
        image_path2 = "images/panther_icon2.png"
        
        if os.path.exists(image_path2):
            st.markdown('<div style="margin-right: 10px;">', unsafe_allow_html=True)
            st.image(image_path2, width=50)
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
    
    # Chat input (with enhanced placeholder from app_eugene.py)
    if user_input := st.chat_input("Where do you want to go today?"):
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate and display assistant response (functionality from app.py)
        with st.chat_message("assistant"):
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

#!/usr/bin/env python3
"""
Demo script showing agent capabilities
Run this to test the agent functions before using in Streamlit
"""

import boto3
from agent_utils import create_agent_tools, process_with_agent

def test_agent_capabilities():
    """Test the agent tools and capabilities"""
    
    print("🤖 Testing Panther Pathfinder Agent Capabilities")
    print("=" * 50)
    
    # Initialize clients
    bedrock_client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # Create tools
    print("🔧 Creating agent tools...")
    tools = create_agent_tools(bedrock_client)
    print(f"✅ Created {len(tools)} tools: {list(tools.keys())}")
    
    # Test individual tools
    print("\n🧪 Testing individual tools:")
    
    # Test time tool
    print("\n⏰ Testing time tool:")
    time_result = tools["get_current_time"]()
    print(f"Current time: {time_result}")
    
    # Test math tool
    print("\n🧮 Testing math tool:")
    math_result = tools["calculate_math"]("10 + 5 * 2")
    print(f"Math result: {math_result}")
    
    # Test text analysis
    print("\n📊 Testing text analysis:")
    analysis_result = tools["analyze_text"]("This is a sample text to analyze for word count")
    print(f"Analysis: {analysis_result}")
    
    # Test agent processing
    print("\n🤖 Testing full agent processing:")
    
    test_queries = [
        "What time is it?",
        "Calculate 15 * 7 + 3",
        "Analyze this text: Hello world this is a test",
        "What is the current company policy on remote work?"  # This will use KB search
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i}: {query} ---")
        try:
            result = process_with_agent(query, tools, bedrock_runtime)
            print(f"Agent Response: {result[:200]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n✅ Agent testing complete!")
    print("\nTo run the full Streamlit app with agent capabilities:")
    print("streamlit run app.py")

if __name__ == "__main__":
    test_agent_capabilities()
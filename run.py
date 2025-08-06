#!/usr/bin/env python3
"""
Startup script for Panther Pathfinder Chatbot
Validates configuration and starts the Streamlit application
"""

import sys
import os
from config import validate_config

def main():
    """Main startup function"""
    print("🐾 Starting Panther Pathfinder - AWS Bedrock Knowledge Base Chatbot")
    print("=" * 60)
    
    # Validate configuration
    print("Validating configuration...")
    if not validate_config():
        print("\n❌ Configuration validation failed!")
        print("Please check your config.py file or environment variables.")
        sys.exit(1)
    
    print("✅ Configuration validated successfully!")
    
    # Start Streamlit app
    print("\n🚀 Starting Streamlit application...")
    print("The app will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the application.")
    print("-" * 60)
    
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()
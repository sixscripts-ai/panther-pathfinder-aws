import os
from typing import Dict, Optional

# AWS Configuration
# You can set these values directly here or use environment variables for security

AWS_CONFIG: Dict[str, Optional[str]] = {
    # AWS Credentials
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    
    # AWS Region
    "region": os.getenv("AWS_REGION", "us-east-1"),
    
    # Bedrock Knowledge Base ID
    "knowledge_base_id": os.getenv("BEDROCK_KNOWLEDGE_BASE_ID"),
    
    # Bedrock Model ID
    "model_id": os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"),
}

# Validation function
def validate_config() -> bool:
    """Validate that all required configuration values are set"""
    required_keys = ["aws_access_key_id", "aws_secret_access_key", "knowledge_base_id"]
    
    missing_keys = []
    for key in required_keys:
        if not AWS_CONFIG.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"Missing required configuration: {', '.join(missing_keys)}")
        print("Please set these values in config.py or as environment variables:")
        for key in missing_keys:
            print(f"  - {key.upper()}")
        return False
    
    return True

# Optional: Set values directly here instead of using environment variables
# Uncomment and fill in your values:

AWS_CONFIG = {
    "aws_access_key_id": "ASIA56MJVV7D6JYMT4642",
    "aws_secret_access_key": "lOVcOjwaqW6SPMBGg89cC8k7eo074tVc7Ett",
    "region": "us-west-2",
    "knowledge_base_id": "I4NGUI2SDB",
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
}

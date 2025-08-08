# 🐾 Panther Pathfinder - AWS Bedrock Knowledge Base Chatbot

A modern Streamlit chatbot interface that integrates with AWS Bedrock Knowledge Base for intelligent document retrieval and AI-powered responses.

## Features

- 🤖 **AI-Powered Chat**: Uses Claude 3 Sonnet via AWS Bedrock for intelligent responses
- 📚 **Knowledge Base Integration**: Retrieves relevant documents from your Bedrock Knowledge Base
- 🔍 **Source Attribution**: Shows document sources for transparency
- 🎨 **Modern UI**: Clean, responsive Streamlit interface
- ⚙️ **Configurable**: Adjustable retrieval settings and model parameters

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS Bedrock Knowledge Base set up
- AWS credentials configured

## Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd panther-pathfinder-aws

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

You have two options for configuration:

#### Option A: Environment Variables (Recommended)
```bash
# Copy the template
cp .env.template .env

# Edit .env with your actual values
nano .env
```

#### Option B: Direct Configuration
Edit `config.py` and uncomment the AWS_CONFIG section at the bottom, filling in your values.

### 3. Required AWS Setup

1. **AWS Bedrock Access**: Ensure your AWS account has access to Bedrock
2. **Knowledge Base**: Create a Bedrock Knowledge Base and note its ID
3. **IAM Permissions**: Your AWS credentials need these permissions:
   - `bedrock:InvokeModel`
   - `bedrock:Retrieve`
   - `bedrock:RetrieveAndGenerate`

## Configuration

Set these required values in your `.env` file or `config.py`:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key  
- `AWS_REGION`: AWS region (default: us-east-1)
- `BEDROCK_KNOWLEDGE_BASE_ID`: Your Bedrock Knowledge Base ID
- `BEDROCK_MODEL_ID`: Model to use (default: Claude 3 Sonnet)

## Usage

### Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Using the Chatbot

1. **Ask Questions**: Type your questions in the chat input
2. **View Sources**: Expand the "Sources" section to see retrieved documents
3. **Adjust Settings**: Use the sidebar to configure retrieval parameters
4. **Clear History**: Use the sidebar button to reset the conversation

## Features in Detail

### Knowledge Base Integration
- Automatically retrieves relevant documents from your Bedrock Knowledge Base
- Shows relevance scores and source document information
- Configurable number of retrieved documents (1-10)

### AI Response Generation
- Uses Claude 3 Sonnet for high-quality responses
- Implements Retrieval-Augmented Generation (RAG) pattern
- Provides context-aware answers based on your documents

### User Interface
- Modern, responsive design
- Chat history persistence during session
- Source attribution for transparency
- Real-time status indicators

## File Structure

```
panther-pathfinder-aws/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── .env.template        # Environment variables template
├── README.md           # This file
└── venv/              # Virtual environment (created locally)
```

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check your AWS credentials and region
2. **Knowledge Base Not Found**: Verify your Knowledge Base ID
3. **Permission Denied**: Ensure your IAM user has required Bedrock permissions
4. **No Results**: Check if your Knowledge Base has indexed documents

### Error Messages

- **"Failed to initialize Bedrock Knowledge Base"**: Check AWS configuration
- **"Error querying knowledge base"**: Verify Knowledge Base ID and permissions
- **"Error generating response"**: Check model access and quotas

## Development

### Adding New Features

The application is modular and easy to extend:

- `BedrockKnowledgeBase` class: Handles AWS Bedrock interactions
- `main()` function: Contains the Streamlit UI logic
- `config.py`: Manages configuration and validation

### Customization

- Modify CSS in the `main()` function for styling changes
- Adjust model parameters in `generate_response_with_rag()`
- Add new sidebar controls for additional features

### Current Limitations
- Due to current LLM limitations, queries are only accurate up to two classes/locations

### Roadmap
- [X] RAG system setup using Amazon Bedrock Knowledge Bases
- [X] Frontend developed using Streamlit
- [X] Python script developed to gather information from Hartnell course catalog (failure of web scraper)
- [X] Gathered information uploaded to S3 buckets
- [X] Python script developed to automatically generate Google Map link to destination
- [X] Multilingual support added
- [ ] Better map integration
- [ ] Make the school databases more AI-accessible (right now, it's very user-focused, but data ingestion is difficult for AI)
- [ ] Build on project to add scalability
- [ ] Automate processes to make it easy to implement across campuses

## Security Notes

- Never commit AWS credentials to version control
- Use environment variables or AWS IAM roles for production
- Rotate access keys regularly
- Follow AWS security best practices

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review AWS Bedrock documentation
3. Open an issue in this repository

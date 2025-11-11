# Azure OpenAI Streamlit Chatbot

## Overview
This repository contains an enterprise-grade OpenAI ChatBot built in Python using the [Streamlit framework](https://streamlit.io/). It integrates with [Azure OpenAI Service (AOAI)](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview) and features comprehensive **Entra ID authentication** for both application and user-level access.

## Key Features

### 🔐 **Enterprise Authentication**
* **Entra ID Integration**: Full Microsoft Entra ID authentication with user login
* **Dual Token Support**: Application service principal + On-Behalf-Of user tokens
* **Security Context**: Comprehensive user tracking and audit logging
* **Session Management**: Secure user session handling with proper token lifecycle

### 🤖 **Advanced Chat Capabilities**
* **Multi-Model Support**: gpt-35-turbo and gpt-4o models
* **Vision Support**: Image upload and analysis with gpt-4o
* **Streaming Responses**: Real-time token streaming for better UX
* **Smart Memory**: Conversation summarization after 7 messages to maintain context
* **Token Tracking**: Detailed usage monitoring for cost management

### 🛠️ **Developer Features**
* **Modular Architecture**: Clean separation of concerns across auth, core, ui, and utils
* **Session State Debugging**: JSON logging for troubleshooting
* **Flexible Configuration**: Environment-based settings management
* **Docker Ready**: Multi-environment container support 

![ChatBot image](./assets/bot_image.png)

## Prerequisites

### Azure Services
1. **Azure Subscription**: Owner permissions on subscription or resource group
2. **Azure OpenAI Service**: [Deployed instance](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal) with:
   - `gpt-35-turbo` deployment (named exactly `gpt-35-turbo`)
   - `gpt-4o` deployment (named exactly `gpt-4o`)

### Entra ID Setup
3. **Application Registration**: [Create an Entra ID app registration](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) with:
   - **Redirect URI**: Set to your application URL (e.g., `http://localhost:8080`)
   - **Client Secret**: Generate for authentication
4. **Service Principal**: [Create service principal](https://learn.microsoft.com/en-us/cli/azure/azure-cli-sp-tutorial-1?tabs=bash) and assign [Cognitive Services OpenAI User role](https://learn.microsoft.com/en-us/azure/role-based-access-control/quickstart-assign-role-user-portal)

### Development Environment
5. **Python 3.12+**: Required for modern async/await support
6. **Docker** (optional): For containerized deployment

## Setup

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd python-streamlit-openai-chatbot

# Create Python virtual environment (3.12+ required)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create your configuration files in the `config/` directory:

> 📝 **Note**: Sample files are provided in `config/sample_files/` for reference.

### 3. Run the Application
Choose your preferred method:

```bash
# Local development (recommended)
python run_app.py

# Direct Streamlit
streamlit run app.py --server.port 8080

### 4. Access the Application
Open your browser to `http://localhost:8080` and authenticate with your Entra ID credentials.

## Architecture Highlights

### 🔐 **Authentication Flow**
- **User Authentication**: Entra ID OAuth2 flow with PKCE
- **Application Authentication**: Client credentials flow for service access
- **On-Behalf-Of (OBO)**: User context preservation through token exchange
- **Security Context**: Comprehensive audit trail with user, IP, and tenant tracking

### 🧩 **Modular Design**
- **Separation of Concerns**: Clear boundaries between auth, UI, core logic, and utilities
- **Dependency Injection**: Configurable clients and token providers
- **State Management**: Centralized Streamlit session state handling
- **Error Handling**: Comprehensive logging and graceful error recovery

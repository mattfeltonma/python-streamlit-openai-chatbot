import logging
import asyncio
import streamlit as st
import os
import sys
import json
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

# Create project root variable which will ensure repo directory will be used when importing modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import custom modules
from src.core import ChatMessage, get_streaming_chat_completion, get_chat_completion
from src.core.chat import setup_assistant
from src.auth import get_access_token_client_credentials, get_access_token_on_behalf_of, EntraUserAuth, UserSecurityContext
from src.utils import setup_logger
from src.ui import create_sidebar, display_chat_messages, display_token_usage, setup_main_page
from src.ui.components import (
    create_user_message_with_image, 
    create_user_message_text_only, 
    remove_image_from_message
)

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


def initialize_session_state():
    """Initialize all session state variables."""
    # Chat-related session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            setup_assistant(),
            {"role": "assistant", "content": "Hello!"}
        ]
    
    # Authentication-related session state
    if "user_authenticated" not in st.session_state:
        st.session_state.user_authenticated = False
    
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None

    if "app_access_token" not in st.session_state:
        st.session_state.app_access_token = None

    if "app_auth_expiry" not in st.session_state:
        st.session_state.app_auth_expiry = None
    
    if "id_token" not in st.session_state:
        st.session_state.id_token = None
    
    if "auth_expiry" not in st.session_state:
        st.session_state.auth_expiry = None
    
    # Security context
    if "security_context" not in st.session_state:
        st.session_state.security_context = None


def check_user_authentication() -> bool:
    """Check if user is authenticated."""
    if "user_authenticated" not in st.session_state:
        st.session_state.user_authenticated = False
    
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
    
    return st.session_state.user_authenticated


def render_login_page():
    """Render the login page for unauthenticated users."""
    st.title("Login Required")
    st.write("Please authenticate with your enterprise Entra ID user account")
    
    # Check for authentication callback
    query_params = st.query_params
    if "code" in query_params:
        handle_auth_callback(query_params["code"])
        return
    
    # Create auth instance
    auth = EntraUserAuth(
        client_id=os.getenv("AZURE_CLIENT_ID"),
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )
    
    try:
        login_url = auth.get_login_url()
        st.markdown(f"[**Click here to login with Microsoft →**]({login_url})")
        
        with st.expander("Authentication Info"):
            st.info(
                "This application uses Microsoft Entra ID for secure authentication. "
                "You'll be redirected to Microsoft's login page."
            )
    except Exception as e:
        st.error(f"Authentication configuration error: {e}")
        logger.error(f"Auth config error: {e}", exc_info=True)


def handle_auth_callback(auth_code: str):
    """Handle the OAuth callback from Entra ID."""
    try:
        auth = EntraUserAuth(
            client_id=os.getenv("AZURE_CLIENT_ID"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            redirect_uri=os.getenv("REDIRECT_URI"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
        
        result = auth.handle_callback(auth_code)
        if result:
            st.session_state.user_authenticated = True
            st.session_state.user_info = result.get("user_info")
            st.session_state.graph_access_token = result.get("access_token")
            st.session_state.id_token = result.get("id_token")  # Store ID token for OnBehalfOf
            st.session_state.auth_expiry = result.get("expires_in")

            result_app = auth.get_application_token() 
            if result_app:
                st.session_state.app_access_token = result_app.get("access_token_app")
                st.session_state.app_auth_expiry = result_app.get("expires_in_app")
            
            # Create security context
            st.session_state.security_context = UserSecurityContext(
                application_name="Azure OpenAI Chatbot",
                end_user_id=st.session_state.user_info.get('id') or st.session_state.user_info.get('userPrincipalName', 'unknown'),
                source_ip=getattr(st.context, "ip_address", None) or "unknown",
                end_user_tenant_id=os.getenv("AZURE_TENANT_ID")
            )
            
            st.success("Authentication successful! Redirecting...")
            st.rerun()  # Refresh to show authenticated app
        else:
            st.error("Authentication failed. Please try again.")
            
    except Exception as e:
        st.error(f"Authentication error: {e}")
        logger.error(f"Auth callback error: {e}", exc_info=True)


def render_top_logout_button():
    """Render logout button in top right corner."""
    if st.session_state.user_authenticated and st.session_state.user_info:
        user = st.session_state.user_info
        
        # Create columns to push logout button to the right
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col2:
            st.write(f"👋 {user.get('displayName', 'User')}")
        
        with col3:
            if st.button("🚪 Logout", type="secondary"):
                logout_user()


def render_user_info_sidebar():
    """Add user information to sidebar (without logout button)."""
    if st.session_state.user_authenticated and st.session_state.user_info:
        user = st.session_state.user_info
        with st.sidebar:
            st.markdown("---")
            st.markdown("### User Info")
            st.write(f"**Name:** {user.get('displayName', 'N/A')}")
            st.write(f"**Email:** {user.get('userPrincipalName', 'N/A')}")


def logout_user():
    """Clear user session and logout."""
    st.session_state.user_authenticated = False
    st.session_state.user_info = None
    st.session_state.auth_token = None
    st.session_state.id_token = None
    st.session_state.auth_expiry = None
    st.session_state.security_context = None
    st.session_state.messages = [
        setup_assistant(),
        {"role": "assistant", "content": "Hello!"}
    ]
    st.rerun()


def create_azure_client(token_provider):
    """Create and return an Azure OpenAI client."""
    return AzureOpenAI(
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider=token_provider
    )


def handle_conversation_length(client, model, max_tokens):
    """Handle conversation length by summarizing if it exceeds threshold."""
    if len(st.session_state.messages) > 7:
        logging.info("Conversation has exceeded maximum threshold. Summarizing conversation...")
        
        message = {
            "role": "user",
            "content": "Summarize the conversation you've had with the user. Ensure you keep the most important points."
        }
        st.session_state.messages.append(message)
        
        chat_message = get_chat_completion(
            client=client, 
            deployment_name=model, 
            messages=st.session_state.messages, 
            max_tokens=max_tokens,
            security_context=st.session_state.get('security_context')
        )
        
        st.session_state.messages.append(
            {"role": "assistant", "content": chat_message.full_response}
        )
        
        # Keep only system message and last 2 messages (summary)
        st.session_state.messages = [
            st.session_state.messages[0]
        ] + st.session_state.messages[-2:]


def process_chat_input(prompt, sidebar_config, client):
    """Process user input and generate response."""
    uploaded_file = sidebar_config['uploaded_file']
    base64_data = sidebar_config['base64_data']
    image_detail = sidebar_config['image_detail']
    streaming = sidebar_config['streaming']
    model = sidebar_config['model']
    max_tokens = sidebar_config['max_tokens']
    status_box = sidebar_config['status_box']
    
    # Add user message to session state
    if uploaded_file is not None:
        user_message = create_user_message_with_image(prompt, base64_data, image_detail)
        st.session_state.messages.append(user_message)
    else:
        user_message = create_user_message_text_only(prompt)
        st.session_state.messages.append(user_message)
        
    # Display user message
    st.chat_message("user").write(prompt)

    # Get AI response
    messages = st.session_state['messages']
    security_context = st.session_state.get('security_context')
    
    if streaming:
        chat_message = asyncio.run(get_streaming_chat_completion(
            client=client,
            deployment_name=model,
            messages=messages,
            max_tokens=max_tokens,
            security_context=security_context
        ))
        
        # Display streaming response (already displayed in get_streaming_chat_completion)
        st.session_state.messages.append(
            {"role": "assistant", "content": chat_message.full_response}
        )
    else:
        chat_message = get_chat_completion(
            client=client, 
            deployment_name=model, 
            messages=messages, 
            max_tokens=max_tokens,
            security_context=security_context
        )
        
        # Display non-streaming response
        st.chat_message("assistant").write(chat_message.full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": chat_message.full_response}
        )

    # Display token usage
    display_token_usage(status_box, chat_message)

    # Clean up image data to save tokens
    if uploaded_file is not None:
        remove_image_from_message(st.session_state.messages, prompt)
        
    # Handle conversation length
    handle_conversation_length(client, model, max_tokens)


def main():
    """Main application entry point with authentication gate."""
    # Setup phase
    load_dotenv('config/.env.local')
    load_dotenv('config/.env.local.secrets')
    
    # Set page config
    st.set_page_config(
        page_title="Azure OpenAI Chatbot",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Dump session state for debugging (you can comment this out when not needed)
    dump_session_state_to_log()
    
    # Authentication gate
    if not st.session_state.user_authenticated:
        render_login_page()
        return
    
    render_top_logout_button()
    
    setup_main_page()
    
    # Create sidebar and get configuration set by the user
    sidebar_config = create_sidebar()

    # Add user info to sidebar
    render_user_info_sidebar()
    
    # Display chat messages
    display_chat_messages(st.session_state.messages)
    
    # Handle user input
    if prompt := st.chat_input():

        if sidebar_config['on_behalf_of']:
            logging.info(st.session_state.app_access_token)
            # Use ID token for OnBehalfOf flow (JWT assertion)
            token_provider = get_access_token_on_behalf_of(
                scope="https://cognitiveservices.azure.com/.default",
                user_assertion=st.session_state.app_access_token
            )

        else:
            # Get a token for the application's service principal
            token_provider = get_access_token_client_credentials(
                scope="https://cognitiveservices.azure.com/.default"
            )

        # Optional: Log user activity
        user_email = st.session_state.user_info.get('userPrincipalName', 'unknown')
        logger.info(f"Chat input from user: {user_email}")
        
        client = create_azure_client(token_provider)

        # Process the user's chat input and include the sidebar configuration to ensure any options are triggered
        process_chat_input(prompt, sidebar_config, client)

        # Dump session state as valid JSON
        try:
            session_data = {}
            for key, value in st.session_state.items():
                try:
                    json.dumps(value)  # Test if serializable
                    session_data[key] = value
                except (TypeError, ValueError):
                    session_data[key] = str(value)  # Convert non-serializable to string
            logging.info(json.dumps(session_data, indent=2, default=str))
        except Exception as e:
            logging.error(f"Failed to dump session state: {e}")

if __name__ == "__main__":
    main()
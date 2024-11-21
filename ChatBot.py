import logging
import asyncio
import streamlit as st
import os
from openai import AzureOpenAI
from chat import get_streaming_chat_completion, get_chat_completion, setup_assistant
from dotenv import load_dotenv
from loggerconfig import setup_logger
from identity import get_access_token
from images import process_image

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

# Import environment variables
load_dotenv('.variables')

# Configure sidebar with additional options
with st.sidebar:
    service_principal = st.selectbox(
        label="Service Principal",
        options=(
            "Service Principal 1",
            "Service Principal 2"
        ),
        placeholder="Service Principal 1",
    )

    model = st.selectbox(
        label="Model",
        options=(
            "gpt-35-turbo",
            "gpt-4o"
        ),
        placeholder="gpt-35-turbo"
    )

    max_tokens = st.number_input(
        label="Max tokens",
        min_value=100,
        max_value=10000,
        value=1000
    )

    streaming = st.checkbox("Streaming")

    if model == "gpt-4o":
        uploaded_file = st.file_uploader(
            "Upload an image", type=("png", "jpeg", "jpg", "gif", "webp"))
        image_detail = st.selectbox(
            label="Image detail",
            options=(
                "low",
                "high"
            ),
            placeholder="low"
        )

        # Process the image
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            base64_data = process_image(
                original_image=bytes_data, image_detail=image_detail)

    else:
        uploaded_file = None

    # Setup status box for token usage
    status_box = st.empty()

# Obtain Entra ID access token
token_provider = get_access_token(
    scope="https://cognitiveservices.azure.com/.default", service_principal=service_principal)

# Setup main page
st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by Azure OpenAI")

# If there aren't any existing messages in the session state, initalize the chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        setup_assistant(),
        {"role": "assistant", "content": "Hello!"}]

# Display the chat messages unless it's a system role
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue 
    if msg["role"] != "assistant":
        
        # If the content is a list, ensure only the text items are included
        if isinstance(msg["content"], list):
            for item in msg["content"]:
                if item["type"] == "text":
                    st.chat_message(msg["role"]).write(item["text"])
        else:
            st.chat_message(msg["role"]).write(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        azure_ad_token_provider=token_provider
    )

    # If there is an uploaded image use a list-based content structure
    if uploaded_file is not None:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_data}",
                            "detail": image_detail
                        }
                    }
                ]
            }
        )
    else:
        # if no image then use the older structure
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    # Write the user's prompt to the chat
    st.chat_message("user").write(prompt)

    # If streaming is enabled, use the streaming chat completion function
    if streaming:
        messages = st.session_state['messages']

        chat_message = asyncio.run(get_streaming_chat_completion(
            client=client,
            deployment_name=model,
            messages=messages,
            max_tokens=max_tokens))
        
        # Grab the response from the model
        assistant_response = chat_message.full_response

        # Grab the token count from the model and display it in the sidebar
        token_count = f"Prompt tokens: {chat_message.prompt_tokens}, Completion tokens: {
            chat_message.completion_tokens}, Total tokens: {chat_message.total_tokens}"

        status_box.markdown(
            f"""
                <div style="background-color: black; padding: 10px; border-radius: 5px;">
                    <p style="color: white;">{token_count}</p>
                </div>
                """,
            unsafe_allow_html=True
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response})
        
    # Handle non-streaming ChatCompletions here
    else:
        messages = st.session_state['messages']
        chat_message = get_chat_completion(
            client=client, deployment_name=model, messages=messages, max_tokens=max_tokens)

        # Grab the response from the model
        assistant_response = chat_message.full_response

        # Grab the token count from the model and display it in the sidebar
        token_count = f"Prompt tokens: {chat_message.prompt_tokens}, Completion tokens: {
            chat_message.completion_tokens}, Total tokens: {chat_message.total_tokens}"

        status_box.markdown(
            f"""
                <div style="background-color: black; padding: 10px; border-radius: 5px;">
                    <p style="color: white;">{token_count}</p>
                </div>
                """,
            unsafe_allow_html=True
        )
        
        # Append the assistant response to the chat messages
        st.session_state.messages.append(
            {"role": "assistant", "content": assistant_response})
        
        # Write out the assistant response
        st.chat_message("assistant").write(assistant_response)

    # Remove the content of the image from the chat message to cut back on token usage for further conversations
    if uploaded_file is not None:
        st.session_state.messages[-2]["content"] = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        uploaded_file = None
        
    # If the conversation is greater than 7 exchanges, summarize the conversation to save on token usage
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
            max_tokens=max_tokens
        )
        
        st.session_state.messages.append(
            {"role": "assistant", "content": chat_message.full_response}
        )
        
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-2:]

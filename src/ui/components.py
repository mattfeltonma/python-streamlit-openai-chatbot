"""
Reusable UI components for the Streamlit chatbot application.
"""

import streamlit as st

def setup_main_page():
    """
    Setup the main page title and caption.
    """
    st.title("My Crappy Chatbot")
    st.caption("Crappy little Chatbot powered by Streamlit")


def display_chat_messages(messages):
    """
    Display chat messages in the Streamlit interface.
    
    Args:
        messages (list): List of message dictionaries with 'role' and 'content' keys
    """
    for msg in messages:
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


def display_token_usage(status_box, chat_message):
    """
    Display token usage information in the sidebar status box.
    
    Args:
        status_box: Streamlit empty container for displaying status
        chat_message: ChatMessage object containing token usage information
    """
    token_count = (
        f"Prompt tokens: {chat_message.prompt_tokens}, "
        f"Completion tokens: {chat_message.completion_tokens}, "
        f"Total tokens: {chat_message.total_tokens}"
    )

    status_box.markdown(
        f"""
        <div style="background-color: black; padding: 10px; border-radius: 5px;">
            <p style="color: white;">{token_count}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def create_user_message_with_image(prompt, base64_data, image_detail):
    """
    Create a user message dictionary that includes both text and image.
    
    Args:
        prompt (str): The text prompt from the user
        base64_data (str): Base64 encoded image data
        image_detail (str): Image detail level ("low" or "high")
        
    Returns:
        dict: Formatted message dictionary for OpenAI API
    """
    return {
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


def create_user_message_text_only(prompt):
    """
    Create a simple text-only user message.
    
    Args:
        prompt (str): The text prompt from the user
        
    Returns:
        dict: Formatted message dictionary
    """
    return {"role": "user", "content": prompt}


def remove_image_from_message(messages, prompt):
    """
    Remove image content from the last user message to save tokens.
    
    Args:
        messages (list): List of chat messages
        prompt (str): Original text prompt
    """
    messages[-2]["content"] = [
        {
            "type": "text", 
            "text": prompt
        }
    ]
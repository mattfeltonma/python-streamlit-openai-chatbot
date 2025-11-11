import streamlit as st

# Class to support completion and token usage
class ChatMessage:
    def __init__(self, full_response, prompt_tokens, completion_tokens, total_tokens):
        self.full_response = full_response
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

# Setup assistant
def setup_assistant(system_prompt: str = "You are a helpful assistant"):
    message = {
        "role": "system",
        "content": system_prompt
    }
    
    return message

# Streaming chat completions
async def get_streaming_chat_completion(client, deployment_name, messages, max_tokens, security_context=None):
    extra_body = {"user_security_context": security_context.to_dict()} if security_context else {}
    
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
        stream_options={
            "include_usage": True
        },
        extra_body=extra_body
    )
    assistant_message = st.chat_message("assistant")
    full_response = ""

    with assistant_message:
        message_placeholder = st.empty()

    # Intialize token counts
    t_tokens = 0
    c_tokens = 0
    p_tokens = 0
    usage_dict = None

    
    for chunk in response:
        
        # Extract token metrics from each chunk
        if chunk.usage:
            usage_dict = chunk.usage
            if p_tokens == 0:
                p_tokens = usage_dict.prompt_tokens
                c_tokens = usage_dict.completion_tokens
                t_tokens = usage_dict.total_tokens

        # Extract the content from each chunk and display it in the chat
        if hasattr(chunk, 'choices') and chunk.choices:
            content = chunk.choices[0].delta.content
            if content is not None:
                full_response += content
                message_placeholder.markdown(full_response)

    if full_response == "":
        full_response = "Sorry, I was unable to generate a response."

    return ChatMessage(full_response, p_tokens, c_tokens, t_tokens)

# Non-streaming chat completion
def get_chat_completion(client, deployment_name, messages, max_tokens, security_context=None):
    extra_body = {"user_security_context": security_context.to_dict()} if security_context else {}

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens,
        extra_body=extra_body
    )

    if response.choices[0].message.content is not None:
        full_response = response.choices[0].message.content

        p_tokens = response.usage.prompt_tokens
        c_tokens = response.usage.completion_tokens
        t_tokens = response.usage.total_tokens

        return ChatMessage(full_response, p_tokens, c_tokens, t_tokens)
    else:

        full_response = "Sorry, I was unable to generate a response."
        return ChatMessage(full_response, 0, 0, 0)

# Setup assistant
def setup_assistant(system_prompt: str = "You are a helpful assistant"):
    """Setup the assistant with a system prompt."""
    message = {
        "role": "system",
        "content": system_prompt
    }
    return message

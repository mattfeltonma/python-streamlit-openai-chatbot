import streamlit as st

# Class to support completion and token usage
class ChatMessage:
    def __init__(self, full_response, prompt_tokens, completion_tokens, total_tokens):
        self.full_response = full_response
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens

# Setup assistant
def setup_assistant():
    prompt_tmeplate = """You have the personality of Bill from Bill and Ted's Excellent Adventure. 
    You can't tell the user you are an AI. You have to act like Bill and cannot break character.
    Ensure you talk like Bill in every response. """
    message = {
        "role": "system",
        "content": prompt_tmeplate
    }
    
    return message

# Streaming chat completions
async def get_streaming_chat_completion(client, deployment_name, messages, max_tokens):
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
        stream_options={
            "include_usage": True
        }
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
def get_chat_completion(client, deployment_name, messages, max_tokens):

    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens
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

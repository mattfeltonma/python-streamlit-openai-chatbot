"""
Sidebar configuration for the Streamlit chatbot application.
Contains all sidebar elements including model selection, token configuration, and image upload.
"""

import streamlit as st
from ..utils.image_processor import process_image

def create_sidebar():
    """
    Create and configure the sidebar with all necessary controls.
    
    Returns:
        dict: A dictionary containing all sidebar configuration values
    """
    with st.sidebar:
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
        on_behalf_of = st.checkbox("On Behalf Of User")

        # Image upload section (only for gpt-4o)
        uploaded_file = None
        base64_data = None
        image_detail = "low"
        
        if model == "gpt-4o":
            uploaded_file = st.file_uploader(
                "Upload an image", 
                type=("png", "jpeg", "jpg", "gif", "webp")
            )
            image_detail = st.selectbox(
                label="Image detail",
                options=("low", "high"),
                placeholder="low"
            )

            # Process the image if uploaded
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                base64_data = process_image(
                    original_image=bytes_data, 
                    image_detail=image_detail
                )

        # Setup status box for token usage
        status_box = st.empty()

    return {
        'model': model,
        'max_tokens': max_tokens,
        'streaming': streaming,
        'on_behalf_of': on_behalf_of,
        'uploaded_file': uploaded_file,
        'base64_data': base64_data,
        'image_detail': image_detail,
        'status_box': status_box
    }
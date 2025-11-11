import logging
import io
import base64
from PIL import Image

def process_image(original_image, image_detail) -> str:
    
    # Get the current image size
    image = Image.open(io.BytesIO(original_image))
    width, height = image.size
    logging.info(f"Original image size: {width}x{height}")

    # If the user chooses high detail, then resize the image to a maximum size of 2048x2048 while maintaining aspect ratio
    if image_detail == "high":
        max_width, max_height = 2048, 2048
        if width > max_width or height > max_height:
            logging.info("Resizing image to a maximum size of 2048x2048")
            width_ratio = max_width / width
            height_ratio = max_height / height
            scaling_factor = min(width_ratio, height_ratio, 1)
            new_width = int(width * scaling_factor)
            new_height = int(height * scaling_factor)

            final_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS)

        else:
            final_image = image
    else:
        final_image = image

    buffered = io.BytesIO()
    final_image.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()

    # Write the base64 data to disk
    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    
    return base64_data

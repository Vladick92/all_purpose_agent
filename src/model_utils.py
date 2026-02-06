from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from utils import *
from pathlib import Path 
import uuid
import streamlit as st

load_dotenv()
api_key=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=api_key)

search_tool=types.Tool(
    google_search=types.GoogleSearch()
)

img_config=types.GenerateImagesConfig(
    number_of_images=1
)

GEN_IMAGES_DIR = Path("generated_images")
GEN_IMAGES_DIR.mkdir(exist_ok=True)

def generate_image_tool(prompt:str):
    """This is tool is for generating images. """
    image_model=st.session_state.image_model
    response=client.models.generate_images(
        model=image_model,
        prompt=prompt,
        config=img_config
    )
    image_bytes=response.generated_images[0].image.image_bytes
    file_name=f'img_{uuid.uuid4().hex[:8]}.png'
    photo_path=GEN_IMAGES_DIR/file_name
    photo_path.write_bytes(image_bytes)
    return {'photo_path':str(photo_path)}

# main_confing=types.GenerateContentConfig(
#     system_instruction="you are helpful AI assistant. Use tool for generating images",
#     tools=[generate_image_tool],
#     temperature=0.7,
#     top_p=0.85,
#     top_k=50,
#     max_output_tokens=1024
#     )

def get_response(user_input,text_model,document=None):
    params=st.session_state.text_model_params
    main_confing=types.GenerateContentConfig(
        system_instruction="you are helpful AI assistant. Use tool for generating images",
        tools=[generate_image_tool],
        **params
    )
    content_list=[user_input]
    if document:
        mime_type= "application/pdf" if document.name.endswith(".pdf") else 'text/plain'
        doc_data=types.Part.from_bytes(
            data=document.getvalue(),
            mime_type=mime_type
        )
        content_list.insert(0,doc_data)
    return client.models.generate_content(
        model=text_model,
        contents=content_list,
        config=main_confing
    )


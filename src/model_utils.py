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

GEN_IMAGES_DIR = Path("generated_images")
GEN_IMAGES_DIR.mkdir(exist_ok=True)

def generate_image_tool(prompt:str):
    """This is tool is for generating images. """
    try:
        image_model=st.session_state.image_model
        image_params=st.session_state.image_model_params
        base_params={
            'number_of_images': 1,
            'aspect_ratio': '1:1'
        }
        if image_model in IMAGE_MODEL_WITH_PARAMS:    
            base_params['image_size']=image_params['image_size']
            base_params['aspect_ratio']=image_params['aspect_ratio']
            base_params['guidance_scale']=image_params['guidance_scale'] 

        image_config=types.GenerateImagesConfig(**base_params)
        response=client.models.generate_images(
            model=image_model,
            prompt=prompt,
            config=image_config
        )
        image_bytes=response.generated_images[0].image.image_bytes
        file_name=f'img_{uuid.uuid4().hex[:8]}.png'
        photo_path=GEN_IMAGES_DIR/file_name
        photo_path.write_bytes(image_bytes)
        return {'photo_path':str(photo_path)}
    except Exception as e:
        raise Exception(f'Mistake in image generation: {str(e)}')

def get_response(user_input,text_model,document=None):
    try: 
        active_tools=[generate_image_tool] if text_model not in TEXT_MODEL_WITHOUT_TOOLS else None
        active_think= types.ThinkingConfig(
            thinking_level=st.session_state.text_model_params['thinking_level']) if text_model in THINKING_MODELS else None
        params=st.session_state.text_model_params
        filtered_params={k:v for k,v in params.items() if k!='thinking_level'}
        main_confing=types.GenerateContentConfig(
            system_instruction=make_system_prompt(text_model),
            tools=active_tools,
            thinking_config=active_think,
            **filtered_params
        )

        content_list=[user_input]
        if document is not None:
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
    except Exception as e:
        raise Exception(f"Mistake in model request {str(e)}")

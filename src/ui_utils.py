import streamlit as st
from model_utils import * 

def session_state_init():
    if 'messages' not in st.session_state:
        st.session_state.messages=[]
    if 'generation' not in st.session_state:
        st.session_state.generation=False

    if 'text_model' not in st.session_state:
        st.session_state.text_model='gemini-2.5-flash-lite'
    if 'image_model' not in st.session_state:
        st.session_state.image_model='imagen-4.0-fast-generate-001'

    if 'optional_file' not in st.session_state:
        st.session_state.optional_file=None

    if 'text_model_params' not in st.session_state:
        st.session_state.text_model_params={
            'temperature': 0.7,
            'top_p': 0.85,
            'top_k': 50,
            'max_output_tokens': 1024
        }

def sidebar_render():
    with st.sidebar:
        with st.expander('Choose model'):
            text_model=st.selectbox(
                "Available text models",
                options=list(AVAILABLE_TEXT_MODELS.keys()),
                disabled=st.session_state.generation,
                help='Models are listed from smallest to smartest, from top to bottom',
                
            )
            st.session_state.text_model=AVAILABLE_TEXT_MODELS[text_model]

            image_model=st.selectbox(
                "Available image models",
                options=list(AVAILABLE_IMAGE_MODELS.keys()),
                disabled=st.session_state.generation,
                help='Models are listed from smallest to smartest, from top to bottom'
            )
            st.session_state.image_model=AVAILABLE_IMAGE_MODELS[image_model]

        selected_file=st.file_uploader(
            "Choose files",
            type=['txt','pdf'],
            max_upload_size=20,
            disabled=st.session_state.generation
        )

        with st.expander('Generation parameters'):
            with st.expander('Text generation'):
                st.session_state.text_model_params['temperature']=st.slider(
                    'Temperature',0.0,2.0,
                    value=st.session_state.text_model_params['temperature'],
                    disabled=st.session_state.generation)
                
                st.session_state.text_model_params['top_p']=st.slider(
                    'Top P',0.0,1.0,
                    value=st.session_state.text_model_params['top_p'],
                    disabled=st.session_state.generation)
                
                st.session_state.text_model_params['top_k']=st.slider(
                    'Top K',1,100,
                    value=st.session_state.text_model_params['top_k'],
                    disabled=st.session_state.generation)
                
                st.session_state.text_model_params['max_output_tokens']=st.slider(
                    'Max tokens for output',128,8196,
                    value=st.session_state.text_model_params['max_output_tokens'],
                    disabled=st.session_state.generation)
                    

        if selected_file: st.session_state.optional_file=selected_file

        if st.button("clear",disabled=st.session_state.generation):
            st.session_state.messages=[]
            st.rerun()

def chat_render():
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            if msg.get('text'):
                st.write(msg['text'])
            if msg.get('photo_path'):
                st.image(msg['photo_path'],
                        caption=f'Image name: {msg['photo_path'].split('/')[1]}')

def assistant_responce(user_input,text_model,file):
    with st.chat_message('assistant'):
        placeholder=st.empty()
        full_resp=''
        current_text=''
        with st.spinner('Thinking',show_time=True):
            responce=get_response(user_input,text_model,file)
            for part in responce.parts:
                if part.text:
                    full_resp+=part.text

            photo_path=get_image_path(responce.automatic_function_calling_history)

        for word in stream_text(full_resp):
            current_text+=word
            placeholder.write(current_text+ "~>")

    st.session_state.messages.append({
        'role': 'assistant',
        'text': full_resp,
        'photo_path': photo_path if photo_path else None
    })
    st.session_state.generation=False
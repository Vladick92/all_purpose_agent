import streamlit as st
from model_utils import * 

# streamlit session state for sharing values across files
def session_state_init():
    
    # all messages from user and model
    if 'messages' not in st.session_state:
        st.session_state.messages=[]

    # additional variable for disabling ui elements during generation
    if 'generation' not in st.session_state:
        st.session_state.generation=False

    # file for model
    if 'optional_file' not in st.session_state:
        st.session_state.optional_file=None

    # current text and images models
    if 'text_model' not in st.session_state:
        st.session_state.text_model='gemini-2.5-flash-lite'
    if 'image_model' not in st.session_state:
        st.session_state.image_model='imagen-4.0-fast-generate-001'

    # current text generation parameters
    if 'text_model_params' not in st.session_state:
        st.session_state.text_model_params={
            'temperature': 0.7,
            'top_p': 0.85,
            'top_k': 50,
            'max_output_tokens': 1024,
            'thinking_level': 'minimal'
        }

    # current image generation parameters
    if 'image_model_params' not in st.session_state:
        st.session_state.image_model_params={
            'aspect_ratio': '1:1',
            'image_size': '1K',
            'guidance_scale': 0.7
        }

# function for rendering whole sidebar
def sidebar_render():
    with st.sidebar:
        # text model picker
        st.markdown(UI_HELP_TEXTS['model_switcher'])
        text_model=st.selectbox(
            "Text model",
            options=list(AVAILABLE_TEXT_MODELS.keys()),
            disabled=st.session_state.generation,
            help=UI_HELP_TEXTS['text_models'],
            
        )
        st.session_state.text_model=AVAILABLE_TEXT_MODELS[text_model]

        # image model picker
        image_model=st.selectbox(
            "Image model",
            options=list(AVAILABLE_IMAGE_MODELS.keys()),
            disabled=st.session_state.generation,
            help=UI_HELP_TEXTS['image_models']
        )
        st.session_state.image_model=AVAILABLE_IMAGE_MODELS[image_model]

        # additional indicators for current state
        st.markdown(UI_HELP_TEXTS['state_indicators'])
        is_lite=st.session_state.text_model not in TEXT_MODEL_WITHOUT_TOOLS
        is_thinking=st.session_state.text_model in THINKING_MODELS
        is_params=st.session_state.image_model in IMAGE_MODEL_WITH_PARAMS

        status_cols=st.columns(3)
        with status_cols[0]:
            if is_lite:
                status_cols[0].success('Image gen tool is on')
            else:
                status_cols[0].error('Image gen tool is off')

        with status_cols[1]:
            if is_thinking:
                status_cols[1].success('Thinking mode is on')
            else:
                status_cols[1].error('Thinking mode is off')
        
        with status_cols[2]:
            if is_params and is_lite:
                status_cols[2].success('Image params is on')
            else:
                status_cols[2].error('Image params is off')

        st.markdown(UI_HELP_TEXTS['file_uploader'])
        selected_file=st.file_uploader(
            "Choose files for model",
            type=['txt','pdf'],
            max_upload_size=20,
            disabled=st.session_state.generation
        )

        if selected_file: st.session_state.optional_file=selected_file

        # elements for changin parameters of generation
        st.markdown(UI_HELP_TEXTS['generation_help'])
        with st.expander('Text generation'):
            st.session_state.text_model_params['temperature']=st.slider(
                'Temperature',0.0,2.0,
                value=st.session_state.text_model_params['temperature'],
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['temperature'])
            
            st.session_state.text_model_params['top_p']=st.slider(
                'Top P',0.0,1.0,
                value=st.session_state.text_model_params['top_p'],
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['top_p'])
            
            st.session_state.text_model_params['top_k']=st.slider(
                'Top K',1,100,
                value=st.session_state.text_model_params['top_k'],
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['top_k'])
            
            st.session_state.text_model_params['max_output_tokens']=st.slider(
                'Max tokens for output',128,8196,
                value=st.session_state.text_model_params['max_output_tokens'],
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['max_output_tokens'])
            
            st.session_state.text_model_params['thinking_level']=st.select_slider(
                "Thinking level",
                options=['minimal','low','medium','high'],
                value=st.session_state.text_model_params['thinking_level'],
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['thinking_level'])
            
        with st.expander('Image generation'):
            st.session_state.image_model_params['aspect_ratio']=st.selectbox(
                'Aspect ratio',
                ['1:1','3:4','4:3','16:9'],
                index=0,
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['aspect_ratio'])

            st.session_state.image_model_params['image_size']=st.selectbox(
                'Size of image',
                ['1K','2K'],
                index=0,
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['image_size'])

            st.session_state.image_model_params['guidance_scale']=st.slider(
                "Guidance scale",
                0.0,10.0,step=0.5,
                value=st.session_state.image_model_params['guidance_scale'],
                disabled=st.session_state.generation,
                help=UI_HELP_TEXTS['guidance_scale'])
            
        if st.button("Clear chat",disabled=st.session_state.generation):
            st.session_state.messages=[]
            st.rerun()

# rendering chat history and displaying photos if present
def chat_render():
    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            if msg.get('text'):
                st.write(msg['text'])
            if msg.get('photo_path'):
                st.image(msg['photo_path'],
                        caption=f'Image name: {msg['photo_path'].split('/')[1]}')


# main ui function for sending request and saving to session state
def assistant_response(user_input,text_model,file):
    with st.chat_message('assistant'):
        placeholder=st.empty()
        full_resp=''
        photo_path=None
        try: 
            with st.spinner('Thinking',show_time=True):
                response=get_response(user_input,text_model,file)
                if not response.parts:
                    full_resp="Im sorry, but i cant answer prompt."
                else:
                    for part in response.parts:
                        if part.text:
                            full_resp+=part.text

                    # using tool if agent from API returned function call alongside text part of response
                    photo_path=get_image_path(response.automatic_function_calling_history)

        except Exception as e:
            full_resp=f'Something went wrong: {str(e)}{'\n'}'

        finally:
            # streaming text with custom function
            current_text=''
            if full_resp:
                for word in stream_text(full_resp):
                    current_text+=word
                    placeholder.write(current_text+ "~>")
                placeholder.write(current_text)

            # saving users and models responses
            st.session_state.messages.append({
                'role': 'assistant',
                'text': full_resp,
                'photo_path': photo_path
            })
            st.session_state.generation=False
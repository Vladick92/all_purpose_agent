from model_utils import *
from utils import *
from ui_utils import *
import streamlit as st

def main():
    # functions from ui_utils.py
    st.title('Im here to help you !')
    session_state_init()
    sidebar_render()
    chat_render()
    
    # getting input from user
    if message:=st.chat_input("Enter: ",disabled=st.session_state.generation):
        st.session_state.messages.append({
            'role': 'user',
            'text': message
        })
        st.session_state.generation=True
        st.rerun()

    # generating response from model
    if st.session_state.generation:
        last_prompt=st.session_state.messages[-1]['text']
        assistant_response(last_prompt,st.session_state.text_model,st.session_state.optional_file)
        st.rerun()

if __name__=="__main__":
    main()


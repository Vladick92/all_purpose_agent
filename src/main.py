from model_utils import *
from utils import *
from ui_utils import *

def main():
    session_state_init()
    sidebar_render()
    chat_render()

    if message:=st.chat_input("Enter: ",disabled=st.session_state.generation):
        st.session_state.messages.append({
            'role': 'user',
            'text': message
        })
        st.session_state.generation=True
        st.rerun()

    if st.session_state.generation:
        last_prompt=st.session_state.messages[-1]['text']
        assistant_responce(last_prompt,st.session_state.text_model,st.session_state.optional_file)
        st.rerun()

if __name__=="__main__":
    main()


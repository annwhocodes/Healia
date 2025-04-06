import streamlit as st
from assistant import FirstResponderAssistant
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown(
   """
   <style>
       html, body, #root, .block-container {
           height: 100vh;
           width: 100vw;
           margin: 0;
           padding: 0;
           overflow: hidden;
            background: radial-gradient(circle, rgba(20, 20, 40, 1) 0%, rgba(10, 10, 20, 1) 100%); /* Radial Gradient Background */
           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
           display: flex;
           justify-content: center;
           align-items: center;
       }
   </style>
   """,
   unsafe_allow_html=True
)
st.title("Let me see if I remember you... This may take some time")

assistant = FirstResponderAssistant()
assistant.start_assistance_flow()
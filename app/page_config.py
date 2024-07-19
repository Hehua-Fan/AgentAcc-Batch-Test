import streamlit as st

def page_config():
    st.set_page_config(page_title="AgentAcc Batch Test", layout="wide", page_icon="🎯")
    
    css = """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 450px;
           max-width: 450px;
       }
       """
    st.markdown(css, unsafe_allow_html=True)
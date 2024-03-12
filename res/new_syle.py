import streamlit as st    
def page_style():
    style = """
    <style>
    .reportview-container {
        background: #f0f0f0;
    }
    .main .block-container {
        max-width: 90%;
        padding-top: 50px;
        padding-right: 50px;
        padding-left: 50px;
        padding-bottom: 50px;
        background-color: ffffdd;
    }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
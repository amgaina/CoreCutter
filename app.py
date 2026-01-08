"""
This is the main application file for the Mid South Extrusion Plastic Core Stock Cutter.
It sets up the Streamlit app configuration, global styles, and renders the header
and main landing page components.
Author: Abhishek Amgain
Company: Mid South Extrusion
Date: January 2026
"""

import streamlit as st
from pages import landing_page, auth
import os 
import sys

# ============================================================================
# PASSWORD PROTECTION
# ============================================================================
auth.check_password()

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

st.set_page_config(
    page_title="Plastic Core Cutter - Mid South Extrusion",
    page_icon=resource_path("mse_logo.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Global white background and black text
st.markdown(
    """
    <style>
    .stApp {
        background: #fff !important;
        color: #000 !important;
    }
    body, p, label, .stMarkdown, .stTextInput>div>input, .stNumberInput>div>input {
        color: #000 !important;
    }
    h2, h3, h4, h5, h6, h1{
        color: #0a4c92 !important;
    }
    /* All buttons - blue background with white text */
    button[kind="primary"], button[kind="secondary"], .stButton>button, .stFormSubmitButton>button {
        background-color: #0a4c92 !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
    }
    button[kind="primary"]:hover, button[kind="secondary"]:hover, .stButton>button:hover, .stFormSubmitButton>button:hover {
        background-color: #083a73 !important;
        color: white !important;
        border: none !important;
    }
    /* Override any conflicting text color rules */
    .stButton>button p, .stFormSubmitButton>button p,
    button[kind="primary"] p, button[kind="secondary"] p {
        color: white !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# Header
landing_page.render_header()

# Body (main content)
landing_page.render_landing_page()
"""
Simple Password Protection for CoreCut
Prevents unauthorized access to the application.

Author: Abhishek Amgain
Company: Mid South Extrusion
Date: January 2026
"""

import streamlit as st


def check_password():
    """
    Username and password check. User must enter correct credentials to access app.
    """
    
    def credentials_entered():
        """Check if username and password are correct."""
        if (st.session_state["username"] == st.secrets["username"] and 
            st.session_state["password"] == st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["username"]  # Remove credentials from memory
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # If credentials already checked in this session, allow access
    if st.session_state.get("password_correct", False):
        return True

    # Show login form
    st.markdown(
        """
        <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.text_input(
        "Username",
        on_change=credentials_entered,
        key="username",
    )
    
    st.text_input(
        "Password",
        type="password",
        on_change=credentials_entered,
        key="password",
    )

    if st.session_state.get("password_correct") == False:
        st.error("❌ Incorrect password. Please try again.")
    
    st.stop()
    return False

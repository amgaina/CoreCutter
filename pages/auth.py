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
    Simple password check. User must enter correct password to access app.
    """
    
    def password_entered():
        """Check if password is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove password from memory
        else:
            st.session_state["password_correct"] = False

    # If password already checked in this session, allow access
    if st.session_state.get("password_correct", False):
        return True

    # Show password input dialog
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
        "Enter Application Password",
        type="password",
        on_change=password_entered,
        key="password",
    )

    if st.session_state.get("password_correct") == False:
        st.error("❌ Incorrect password. Please try again.")
    
    st.stop()
    return False

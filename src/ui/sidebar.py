"""
Sidebar UI component for the Medical Assistant app.
"""
import streamlit as st
from src.auth.authentication import (
    login, logout, authenticate, get_current_user, 
    register_user, toggle_signup_form
)

def show_sidebar():
    """
    Display the sidebar with authentication controls and app information.
    """
    with st.sidebar:
        st.title("Medical Assistant")
        st.markdown("---")
        
        # Authentication section
        if not authenticate():
            if not st.session_state.get('show_signup', False):
                # Login form
                st.subheader("Login")
                with st.form(key="login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit_button = st.form_submit_button(label="Login")
                    
                if submit_button:
                    if login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                
                # Link to signup form
                st.markdown("New user? [Create an account](#)")
                if st.button("Sign Up"):
                    toggle_signup_form()
                    st.rerun()
            else:
                # Sign up form
                st.subheader("Create an Account")
                with st.form(key="signup_form"):
                    new_username = st.text_input("Choose a Username")
                    new_password = st.text_input("Create a Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    signup_button = st.form_submit_button(label="Register")
                    
                if signup_button:
                    success, message = register_user(
                        new_username, new_password, confirm_password
                    )
                    if success:
                        st.success(message)
                        # Automatically switch back to login form
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error(message)
                
                # Link back to login
                st.markdown("Already have an account? [Log in](#)")
                if st.button("Back to Login"):
                    toggle_signup_form()
                    st.rerun()
        else:
            st.success(f"Logged in as: {get_current_user()}")
            if st.button("Logout"):
                logout()
                st.rerun()
        
        st.markdown("---")
        
        # App information
        st.subheader("About")
        st.markdown("""
        This Medical Assistant provides information about:
        - Alternative medications
        - Generic medicine options
        - Medicine finder

        Powered by Groq LLM and MCP tools.
        """)
        
        # Version information
        st.markdown("---")
        st.caption("Version 1.0.0")
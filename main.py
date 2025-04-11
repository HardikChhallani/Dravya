"""
Main entry point for the Streamlit-based Medical Assistant app.
"""
import streamlit as st
from src.auth.authentication import initialize_auth, authenticate
from src.ui.alternatives import show_alternatives_tab
from src.ui.generic_medicines import show_generic_medicines_tab
from src.ui.medicine_finder import show_medicine_finder_tab
from src.ui.sidebar import show_sidebar

def main():
    """
    Main function that initializes and runs the Streamlit app.
    """
    # Set page configuration
    st.set_page_config(
        page_title="Medical Assistant",
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize authentication
    initialize_auth()

    # Show sidebar (contains login/logout)
    show_sidebar()

    # Check if user is authenticated
    if not authenticate():
        st.info("Please log in to access the Medical Assistant.")
        return

    # Once authenticated, show the main application
    st.title("Medical Assistant")
    
    # Create tabs for different functionalities
    tabs = st.tabs(["Alternatives", "Generic Medicines", "Find Your Medicines"])
    
    with tabs[0]:
        show_alternatives_tab()
    
    with tabs[1]:
        show_generic_medicines_tab()
    
    with tabs[2]:
        show_medicine_finder_tab()

if __name__ == "__main__":
    main()
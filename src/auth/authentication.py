"""
Authentication module for handling user login, registration, and session management.
"""
import streamlit as st
import hashlib
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# File to store registered users (in a real app, use a proper database)
USERS_FILE = Path("users.json")

def initialize_auth():
    """
    Initialize the authentication system by setting up session state variables.
    """
    # Initialize session state variables if they don't exist
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    
    # Load users from file
    if 'users' not in st.session_state:
        # Default users (will be overwritten if users file exists)
        st.session_state.users = {
            'admin': (
                '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
                ''  # admin password: admin
            ),
            'user': (
                '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb',
                ''  # user password: user
            )
        }
        
        # Try to load users from file
        load_users()

def save_users():
    """
    Save users to a JSON file.
    """
    try:
        # Convert the format to be JSON serializable
        users_dict = {}
        for username, (password_hash, salt) in st.session_state.users.items():
            users_dict[username] = {
                "password_hash": password_hash,
                "salt": salt
            }
            
        with open(USERS_FILE, 'w') as f:
            json.dump(users_dict, f)
    except Exception as e:
        st.error(f"Failed to save users: {e}")

def load_users():
    """
    Load users from a JSON file.
    """
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r') as f:
                users_dict = json.load(f)
                
            # Convert back to internal format
            users = {}
            for username, data in users_dict.items():
                users[username] = (data["password_hash"], data.get("salt", ""))
                
            st.session_state.users = users
        except Exception as e:
            st.error(f"Failed to load users: {e}")

def hash_password(password, salt=""):
    """
    Hash the password with the given salt using SHA-256.
    
    Args:
        password (str): The password to hash
        salt (str): Salt to add to the password
        
    Returns:
        str: The hashed password
    """
    return hashlib.sha256((password + salt).encode()).hexdigest()

def login(username, password):
    """
    Attempt to log in a user with the given credentials.
    
    Args:
        username (str): Username
        password (str): Password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    if username in st.session_state.users:
        stored_hash, salt = st.session_state.users[username]
        if hash_password(password, salt) == stored_hash:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.login_time = datetime.now()
            return True
    return False

def register_user(username, password, confirm_password):
    """
    Register a new user.
    
    Args:
        username (str): Username
        password (str): Password
        confirm_password (str): Password confirmation
        
    Returns:
        tuple: (success_status, message)
    """
    # Validate inputs
    if not username or not password or not confirm_password:
        return False, "All fields are required"
    
    if username in st.session_state.users:
        return False, "Username already exists"
    
    if password != confirm_password:
        return False, "Passwords do not match"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    # Create new user
    salt = ""  # In a real app, generate a random salt
    password_hash = hash_password(password, salt)
    st.session_state.users[username] = (password_hash, salt)
    
    # Save users to file
    save_users()
    
    return True, "Registration successful! You can now log in."

def logout():
    """
    Log out the current user by resetting session state.
    """
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_time = None

def authenticate():
    """
    Check if the user is authenticated and the session is valid.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    # If not authenticated, return False
    if not st.session_state.authenticated:
        return False
    
    # Check if session has expired (8 hour timeout)
    if st.session_state.login_time:
        session_duration = datetime.now() - st.session_state.login_time
        if session_duration > timedelta(hours=8):
            # Session expired, log out
            logout()
            return False
    
    return True

def get_current_user():
    """
    Get the currently logged-in username.
    
    Returns:
        str: Username or None if not logged in
    """
    return st.session_state.username if authenticate() else None

def toggle_signup_form():
    """Toggle the visibility of the signup form."""
    st.session_state.show_signup = not st.session_state.show_signup
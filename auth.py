import streamlit as st
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
import re
import json

class AuthSystem:
    def __init__(self, db_path="data/user_progress.db"):
        self.db_path = db_path
        self._init_auth_tables()
    
    def _init_auth_tables(self):
        """Initialize authentication database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Users table - fixed SQL syntax
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     email TEXT UNIQUE NOT NULL,
                     password_hash TEXT NOT NULL,
                     salt TEXT NOT NULL,
                     role TEXT DEFAULT 'student',
                     is_verified INTEGER DEFAULT 1,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     last_login TIMESTAMP,
                     profile_data TEXT DEFAULT '{}')''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return password_hash, salt
    
    def _verify_password(self, password, password_hash, salt):
        """Verify password against hash"""
        test_hash, _ = self._hash_password(password, salt)
        return test_hash == password_hash
    
    def _validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one digit"
        return True, "Password is strong"
    
    def register_user(self, username, email, password, confirm_password):
        """Register a new user"""
        # Validation checks
        if not username or not email or not password:
            return False, "All fields are required"
        
        if password != confirm_password:
            return False, "Passwords do not match"
        
        if not self._validate_email(email):
            return False, "Invalid email format"
        
        is_valid, message = self._validate_password(password)
        if not is_valid:
            return False, message
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        # Check if username or email already exists
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if c.fetchone():
            conn.close()
            return False, "Username or email already exists"
        
        # Create user
        password_hash, salt = self._hash_password(password)
        
        try:
            c.execute('''INSERT INTO users (username, email, password_hash, salt, is_verified)
                        VALUES (?, ?, ?, ?, 1)''',
                     (username, email, password_hash, salt))
            
            user_id = c.lastrowid
            
            # Initialize user progress in gamification system
            try:
                from gamification import game_engine
                game_engine._init_user_progress(str(user_id))
            except Exception as e:
                print(f"Warning: Could not initialize gamification progress: {e}")
            
            conn.commit()
            conn.close()
            
            return True, "Registration successful! You can now login."
            
        except sqlite3.Error as e:
            conn.close()
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get user data
        c.execute('''SELECT id, username, password_hash, salt, role 
                    FROM users WHERE username = ? OR email = ?''', (username, username))
        user_data = c.fetchone()
        
        if not user_data:
            conn.close()
            return False, "Invalid username or password"
        
        user_id, db_username, password_hash, salt, role = user_data
        
        # Verify password
        if not self._verify_password(password, password_hash, salt):
            conn.close()
            return False, "Invalid username or password"
        
        # Update last login
        c.execute('''UPDATE users SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = ?''', (user_id,))
        
        conn.commit()
        conn.close()
        
        # Store session in Streamlit session state
        st.session_state.user_id = user_id
        st.session_state.username = db_username
        st.session_state.role = role
        st.session_state.is_authenticated = True
        
        return True, "Login successful!"
    
    def logout_user(self):
        """Log out current user"""
        for key in ['user_id', 'username', 'role', 'is_authenticated']:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_current_user(self):
        """Get current user data"""
        if not st.session_state.get('is_authenticated', False):
            return None
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT id, username, email, role, created_at, last_login, profile_data
                    FROM users WHERE id = ?''', (st.session_state.user_id,))
        
        user_data = c.fetchone()
        conn.close()
        
        if user_data:
            return {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'role': user_data[3],
                'created_at': user_data[4],
                'last_login': user_data[5],
                'profile_data': json.loads(user_data[6]) if user_data[6] else {}
            }
        
        return None

# Authentication UI Components
def render_login_register_forms():
    """Render login and registration forms"""
    
    # Check if user is already logged in
    if st.session_state.get('is_authenticated', False):
        auth = AuthSystem()
        user_data = auth.get_current_user()
        if user_data:
            st.success(f"Welcome back, {user_data['username']}!")
            return
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_register_form()

def render_login_form():
    """Render login form"""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login", type="primary"):
            if username and password:
                auth = AuthSystem()
                success, message = auth.login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Please fill in all fields")

def render_register_form():
    """Render registration form"""
    st.subheader("Create New Account")
    
    with st.form("register_form"):
        username = st.text_input("Username", help="At least 3 characters")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", 
                               help="At least 8 characters with uppercase, lowercase, and numbers")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Terms agreement
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        if st.form_submit_button("Register", type="primary"):
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all fields")
            elif not agree_terms:
                st.error("Please agree to the Terms of Service")
            else:
                auth = AuthSystem()
                success, message = auth.register_user(username, email, password, confirm_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def initialize_auth():
    """Initialize authentication state"""
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

# Global auth instance
auth_system = AuthSystem()
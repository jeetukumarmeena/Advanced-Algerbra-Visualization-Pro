"""
Algebra Visualizer Pro - Advanced Interactive Algebra Learning Platform

A comprehensive Streamlit-based platform for learning and visualizing 
algebra concepts with interactive tools, progress tracking, and AI features.

Version: 2.0.0
Author: Algebra Visualizer Team
License: MIT
"""

__version__ = "2.0.0"
__author__ = "Algebra Visualizer Team"
__email__ = "contact@algebra-visualizer.com"
__license__ = "MIT"

# Package imports for easy access
from .config import config
from .auth import AuthSystem, auth_system, render_login_register_forms, require_auth
from .database import DatabaseManager, db_manager
from .math_engine import MathEngine, math_engine
from .visualizations import Visualizations, viz
from .gamification import GamificationEngine, game_engine
from .voice_commands import VoiceCommandSystem, voice_system
from .export_utils import ExportManager, export_manager
from .themes import THEMES, get_theme_css

# Main application class
from .app import AlgebraVisualizerApp

# Utility functions
def initialize_platform():
    """Initialize the complete algebra platform"""
    import streamlit as st
    from .auth import initialize_auth
    from .database import DatabaseManager
    
    # Initialize authentication
    initialize_auth()
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Initialize session state
    if 'platform_initialized' not in st.session_state:
        st.session_state.platform_initialized = True
        st.session_state.current_section = "Dashboard"
        st.session_state.learning_mode = "Intermediate"
        st.session_state.theme = "Professional Dark"
    
    return True

def get_platform_info():
    """Get platform information and statistics"""
    return {
        "version": __version__,
        "features": [
            "Interactive Algebra Learning",
            "Real-time Visualizations", 
            "Progress Tracking & Gamification",
            "Voice Command System",
            "Export & Reporting",
            "Multi-theme Support",
            "User Authentication",
            "AI-powered Explanations"
        ],
        "supported_formats": ["PDF", "PNG", "CSV", "JSON", "HTML"],
        "math_areas": [
            "Algebra Basics",
            "Quadratic Equations", 
            "Polynomials",
            "Calculus",
            "Geometry",
            "Word Problems"
        ]
    }

def check_dependencies():
    """Check if all required dependencies are available"""
    import importlib
    import sys
    
    required_packages = {
        'streamlit': 'Web application framework',
        'numpy': 'Numerical computations',
        'pandas': 'Data manipulation',
        'plotly': 'Interactive visualizations',
        'sympy': 'Symbolic mathematics',
        'matplotlib': 'Static plotting',
        'PIL': 'Image processing',
        'reportlab': 'PDF generation'
    }
    
    missing = []
    available = []
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            available.append((package, description, "✅"))
        except ImportError:
            missing.append((package, description, "❌"))
    
    return {
        "available": available,
        "missing": missing,
        "all_available": len(missing) == 0
    }

# Error classes
class AlgebraVisualizerError(Exception):
    """Base exception for Algebra Visualizer"""
    pass

class MathEngineError(AlgebraVisualizerError):
    """Math computation related errors"""
    pass

class VisualizationError(AlgebraVisualizerError):
    """Plotting and visualization errors"""
    pass

class DatabaseError(AlgebraVisualizerError):
    """Database operation errors"""
    pass

class AuthError(AlgebraVisualizerError):
    """Authentication and authorization errors"""
    pass

# Constants
SUPPORTED_BROWSERS = ["Chrome", "Firefox", "Safari", "Edge"]
SUPPORTED_DEVICES = ["Desktop", "Tablet", "Mobile"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Platform configuration defaults
DEFAULT_CONFIG = {
    "theme": "Professional Dark",
    "auto_save": True,
    "notifications": True,
    "voice_commands": True,
    "difficulty": "Intermediate",
    "language": "English"
}

# Export the main application runner
def run_app():
    """Run the main Algebra Visualizer application"""
    from .app import AlgebraVisualizerApp
    app = AlgebraVisualizerApp()
    app.run()

# Make essential classes available at package level
__all__ = [
    # Core classes
    'AlgebraVisualizerApp',
    'MathEngine', 
    'Visualizations',
    'DatabaseManager',
    'AuthSystem',
    'GamificationEngine',
    'VoiceCommandSystem',
    'ExportManager',
    
    # Instances
    'math_engine',
    'viz', 
    'db_manager',
    'auth_system',
    'game_engine',
    'voice_system',
    'export_manager',
    
    # Functions
    'initialize_platform',
    'get_platform_info',
    'check_dependencies',
    'run_app',
    'render_login_register_forms',
    'require_auth',
    
    # Constants
    'THEMES',
    'get_theme_css',
    'config'
]

print(f"Algebra Visualizer Pro {__version__} initialized successfully!")
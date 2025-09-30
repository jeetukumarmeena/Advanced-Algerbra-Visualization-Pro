import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App Configuration
    APP_NAME = "Advanced Algebra Visualizer Pro"
    VERSION = "2.0.0"
    
    # Theme Settings
    DEFAULT_THEME = "Professional Dark"
    AVAILABLE_THEMES = ["Professional Dark", "Math Classic", "Cyberpunk", "Light Academic"]
    
    # Math Settings
    DEFAULT_PRECISION = 4
    MAX_PLOT_POINTS = 1000
    CACHE_TIMEOUT = 3600  # 1 hour
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "algebra-visualizer-secret-key-2024")
    
    # Database
    DATABASE_PATH = "data/user_progress.db"
    
    # Features
    ENABLE_VOICE_COMMANDS = True
    ENABLE_GAMIFICATION = True
    ENABLE_ANALYTICS = True

config = Config()
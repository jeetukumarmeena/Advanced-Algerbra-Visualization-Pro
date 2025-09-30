THEMES = {
    "Professional Dark": {
        "primary": "#4FD1C7",
        "secondary": "#38B2AC", 
        "accent": "#81E6D9",
        "background": "#1A202C",
        "text": "#E2E8F0",
        "card_bg": "#2D3748",
        "success": "#68D391",
        "warning": "#F6E05E",
        "error": "#FC8181"
    },
    "Math Classic": {
        "primary": "#E53E3E",
        "secondary": "#C53030",
        "accent": "#F56565", 
        "background": "#F7FAFC",
        "text": "#2D3748",
        "card_bg": "#FFFFFF",
        "success": "#38A169",
        "warning": "#D69E2E",
        "error": "#E53E3E"
    },
    "Cyberpunk": {
        "primary": "#00FF88",
        "secondary": "#FF0088", 
        "accent": "#8800FF",
        "background": "#000000",
        "text": "#FFFFFF",
        "card_bg": "#111111",
        "success": "#00FFFF",
        "warning": "#FF6B6B",
        "error": "#FF0000"
    },
    "Light Academic": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "accent": "#F18F01",
        "background": "#F8F9FA", 
        "text": "#212529",
        "card_bg": "#FFFFFF",
        "success": "#4CAF50",
        "warning": "#FFC107",
        "error": "#F44336"
    }
}

def get_theme_css(theme_name):
    theme = THEMES.get(theme_name, THEMES["Professional Dark"])
    
    return f"""
    <style>
    :root {{
        --primary: {theme['primary']};
        --secondary: {theme['secondary']};
        --accent: {theme['accent']};
        --background: {theme['background']};
        --text: {theme['text']};
        --card-bg: {theme['card_bg']};
        --success: {theme['success']};
        --warning: {theme['warning']};
        --error: {theme['error']};
    }}
    
    .main-header {{
        font-size: 3.5rem;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
    }}
    
    .formula-card {{
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        border-left: 6px solid var(--primary);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .formula-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }}
    
    .section-header {{
        color: var(--primary);
        border-bottom: 4px solid var(--primary);
        padding-bottom: 0.8rem;
        margin-top: 3rem;
        font-size: 2.2rem;
        font-weight: 700;
    }}
    
    .concept-pill {{
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        margin: 0.5rem;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .concept-pill:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    
    .problem-solver {{
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid var(--primary);
        margin: 1rem 0;
    }}
    
    .step-by-step {{
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }}
    
    body {{
        background-color: var(--background);
        color: var(--text);
        transition: all 0.3s ease;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    
    </style>
    """
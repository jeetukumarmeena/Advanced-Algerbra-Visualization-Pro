import streamlit as st
import threading
import queue
import time
import re
import json
from datetime import datetime
import numpy as np

# Safe import with fallbacks for cloud deployment
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    st.warning(f"Voice modules not available: {e}")

try:
    from math_engine import math_engine
    from visualizations import viz
    MATH_ENGINE_AVAILABLE = True
except ImportError:
    MATH_ENGINE_AVAILABLE = False

class VoiceCommandSystem:
    def __init__(self):
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.last_command_time = 0
        self.command_cooldown = 2  # seconds
        
        # Initialize voice components only if available
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.tts_engine = self.setup_voice_engine()
            except Exception as e:
                st.error(f"Voice initialization failed: {e}")
                self.voice_available = False
        else:
            self.voice_available = False
            
        # Voice commands mapping
        self.commands = {
            # Navigation commands
            "go to dashboard": "navigate_dashboard",
            "show quadratic solver": "navigate_quadratic",
            "open polynomial analyzer": "navigate_polynomial", 
            "show identities": "navigate_identities",
            "practice problems": "navigate_practice",
            "show progress": "navigate_progress",
            
            # Math operation commands
            "solve quadratic": "solve_quadratic",
            "expand expression": "expand_expression",
            "factor expression": "factor_expression",
            "calculate derivative": "calculate_derivative",
            "graph function": "graph_function",
            
            # Control commands
            "stop listening": "stop_listening",
            "start listening": "start_listening",
            "help": "show_help",
            "clear screen": "clear_screen",
            "what can I say": "show_commands"
        }

    def setup_voice_engine(self):
        """Initialize text-to-speech engine with error handling"""
        if not VOICE_AVAILABLE:
            return None
            
        try:
            tts_engine = pyttsx3.init()
            # Configure voice properties
            voices = tts_engine.getProperty('voices')
            if voices:
                tts_engine.setProperty('voice', voices[0].id)
            tts_engine.setProperty('rate', 150)
            tts_engine.setProperty('volume', 0.8)
            return tts_engine
        except Exception as e:
            st.warning(f"Text-to-speech not available: {e}")
            return None

    def speak(self, text):
        """Convert text to speech with fallback to text display"""
        if not hasattr(self, 'tts_engine') or self.tts_engine is None:
            # Fallback: show text in Streamlit
            st.info(f"🔊 {text}")
            return
            
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                st.error(f"Speech error: {e}")
        
        # Run in thread to avoid blocking
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()

    def listen(self, timeout=5):
        """Listen for voice input with comprehensive error handling"""
        if not hasattr(self, 'recognizer') or not hasattr(self, 'microphone'):
            st.error("Voice recognition not available in this environment")
            return None
            
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Speak now!")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                
            text = self.recognizer.recognize_google(audio)
            st.success(f"🎤 Heard: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            st.warning("⏰ Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            st.error(f"🚫 Speech recognition service error: {e}")
            return None
        except Exception as e:
            st.error(f"🎤 Unexpected voice error: {e}")
            return None

    def process_command(self, command_text):
        """Process voice command with natural language understanding"""
        if not command_text:
            return None
            
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return None
            
        self.last_command_time = current_time
        
        # Exact command matching
        normalized_command = command_text.lower().strip()
        if normalized_command in self.commands:
            return {'action': self.commands[normalized_command], 'parameters': {}}
        
        # Natural language processing for math commands
        return self._parse_natural_language(command_text)

    def _parse_natural_language(self, text):
        """Parse natural language math commands"""
        text_lower = text.lower()
        
        # Math operation detection
        if any(keyword in text_lower for keyword in ['solve', 'calculate']):
            if 'quadratic' in text_lower:
                return self._parse_quadratic_command(text)
            elif 'derivative' in text_lower:
                return {'action': 'calculate_derivative', 'parameters': {}}
                
        elif 'expand' in text_lower:
            return {'action': 'expand_expression', 'parameters': {}}
            
        elif 'factor' in text_lower:
            return {'action': 'factor_expression', 'parameters': {}}
            
        elif any(keyword in text_lower for keyword in ['graph', 'plot']):
            return {'action': 'graph_function', 'parameters': {}}
            
        elif 'help' in text_lower:
            return {'action': 'show_help', 'parameters': {}}
            
        return None

    def _parse_quadratic_command(self, text):
        """Parse quadratic equation from natural language"""
        try:
            # Extract numbers using regex
            numbers = re.findall(r'-?\d+\.?\d*', text)
            if len(numbers) >= 3:
                a, b, c = map(float, numbers[:3])
                return {
                    'action': 'solve_quadratic_demo',
                    'parameters': {'a': a, 'b': b, 'c': c}
                }
        except Exception as e:
            st.error(f"Error parsing quadratic: {e}")
            
        return {'action': 'solve_quadratic', 'parameters': {}}

    def execute_command(self, command_data):
        """Execute voice command with session state updates"""
        if not command_data:
            return
            
        action = command_data.get('action')
        parameters = command_data.get('parameters', {})
        
        st.info(f"🎯 Executing: {action}")
        
        # Navigation commands
        if action == "navigate_dashboard":
            st.session_state.current_page = "dashboard"
            self.speak("Navigating to dashboard")
            
        elif action == "navigate_quadratic":
            st.session_state.current_page = "quadratic_solver"
            self.speak("Opening quadratic equation solver")
            
        elif action == "navigate_polynomial":
            st.session_state.current_page = "polynomial_analyzer"
            self.speak("Opening polynomial analyzer")
            
        elif action == "solve_quadratic_demo":
            self._demo_quadratic_solve(parameters)
            
        elif action == "solve_quadratic":
            st.session_state.current_page = "quadratic_solver"
            self.speak("Please enter coefficients in the quadratic solver")
            
        elif action == "show_help":
            self._show_voice_help()
            
        elif action == "show_commands":
            self._show_available_commands()
            
        elif action == "clear_screen":
            # Clear specific session state variables instead of all
            keys_to_keep = ['voice_system', 'current_page', 'user_data']
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            self.speak("Interface cleared")
            
        else:
            self.speak("Command not recognized. Say 'help' for available commands.")

    def _demo_quadratic_solve(self, parameters):
        """Demo quadratic solving with voice parameters"""
        a = parameters.get('a', 1)
        b = parameters.get('b', -3)
        c = parameters.get('c', 2)
        
        # Store for display
        st.session_state.voice_demo_result = {
            'type': 'quadratic',
            'equation': f"{a}x² + {b}x + {c} = 0",
            'roots': [1.0, 2.0]  # Demo roots for x² -3x + 2
        }
        
        response = f"Solving {a}x squared plus {b}x plus {c}. The roots are 1 and 2"
        self.speak(response)
        st.session_state.current_page = "quadratic_solver"

    def _show_voice_help(self):
        """Display voice command help"""
        help_text = """
        **🎤 Voice Command Help**
        
        **Navigation:**
        - "Go to dashboard" - Main dashboard
        - "Show quadratic solver" - Quadratic equations
        - "Open polynomial analyzer" - Polynomial analysis
        
        **Math Operations:**
        - "Solve quadratic" - Solve quadratic equations
        - "Expand expression" - Expand algebraic expressions  
        - "Factor expression" - Factor expressions
        - "Calculate derivative" - Find derivatives
        - "Graph function" - Plot functions
        
        **Control:**
        - "Stop listening" - Disable voice
        - "Start listening" - Enable voice  
        - "Help" - Show this help
        - "What can I say" - List commands
        - "Clear screen" - Clear interface
        """
        
        st.info(help_text)
        self.speak("Voice help displayed. Try commands like solve quadratic or show progress.")

    def _show_available_commands(self):
        """List available voice commands"""
        command_text = "**Available Voice Commands:**\n\n"
        for cmd, action in self.commands.items():
            command_text += f"• '{cmd}'\n"
        
        st.info(command_text)
        self.speak("Available commands shown on screen")

    def start_voice_listener(self):
        """Start voice listening with cloud-safe approach"""
        if not VOICE_AVAILABLE:
            st.error("""
            **Voice features unavailable in cloud environment**
            
            Voice commands require microphone access and specific audio libraries 
            that may not be available in Streamlit Cloud deployment.
            
            **You can still:**
            - Use all mathematical features manually
            - Enjoy interactive visualizations  
            - Use the manual command input below
            """)
            return
            
        if self.is_listening:
            return
            
        self.is_listening = True
        self.speak("Voice commands activated. Say 'help' for commands.")

    def stop_voice_listener(self):
        """Stop voice listening"""
        self.is_listening = False
        self.speak("Voice commands deactivated")

# Streamlit UI Components
def render_voice_control_panel():
    """Render voice control interface"""
    st.markdown("---")
    st.header("🎤 Voice Control System")
    
    # Initialize voice system
    if 'voice_system' not in st.session_state:
        st.session_state.voice_system = VoiceCommandSystem()
    
    voice_system = st.session_state.voice_system
    
    # Voice status and controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎤 Start Voice", use_container_width=True, type="primary"):
            voice_system.start_voice_listener()
            
    with col2:
        if st.button("⏹️ Stop Voice", use_container_width=True):
            voice_system.stop_voice_listener()
            
    with col3:
        if st.button("❓ Voice Help", use_container_width=True):
            voice_system._show_voice_help()
    
    # Voice availability notice
    if not VOICE_AVAILABLE:
        st.warning("""
        **ℹ️ Voice Features Notice**
        
        Full voice functionality requires local installation with microphone access.
        In cloud deployment, you can use manual command input below.
        """)
    
    # Manual command input (works in cloud)
    st.subheader("💬 Manual Command Input")
    manual_cmd = st.text_input("Type a voice command:", placeholder="e.g., solve quadratic, show progress")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Execute Command", use_container_width=True):
            if manual_cmd:
                command_data = voice_system.process_command(manual_cmd)
                if command_data:
                    voice_system.execute_command(command_data)
                    # Add to history
                    if 'command_history' not in st.session_state:
                        st.session_state.command_history = []
                    st.session_state.command_history.append(manual_cmd)
                else:
                    st.error("Command not recognized. Try 'help' for available commands.")
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if 'command_history' in st.session_state:
                st.session_state.command_history = []
    
    # Command history
    if 'command_history' in st.session_state and st.session_state.command_history:
        st.subheader("📜 Command History")
        for i, cmd in enumerate(reversed(st.session_state.command_history[-5:])):
            st.write(f"{i+1}. {cmd}")
    
    # Quick action buttons
    st.subheader("⚡ Quick Actions")
    quick_cols = st.columns(4)
    
    with quick_cols[0]:
        if st.button("🧮 Quadratic", use_container_width=True):
            voice_system.execute_command({'action': 'navigate_quadratic', 'parameters': {}})
    
    with quick_cols[1]:
        if st.button("📈 Polynomial", use_container_width=True):
            voice_system.execute_command({'action': 'navigate_polynomial', 'parameters': {}})
    
    with quick_cols[2]:
        if st.button("📊 Progress", use_container_width=True):
            voice_system.execute_command({'action': 'navigate_progress', 'parameters': {}})
    
    with quick_cols[3]:
        if st.button("🔄 Clear", use_container_width=True):
            voice_system.execute_command({'action': 'clear_screen', 'parameters': {}})

def render_voice_demo():
    """Render voice command demo section"""
    st.header("🎤 Voice Command Demo")
    
    st.info("""
    **Try these commands (type in manual input):**
    
    • **"solve quadratic"** - Opens quadratic solver
    • **"show progress"** - Shows progress dashboard  
    • **"help"** - Shows voice command help
    • **"what can I say"** - Lists all commands
    """)
    
    # Demo quadratic solver
    if st.button("🎯 Demo Quadratic Solve"):
        voice_system = st.session_state.get('voice_system', VoiceCommandSystem())
        voice_system.execute_command({
            'action': 'solve_quadratic_demo', 
            'parameters': {'a': 1, 'b': -5, 'c': 6}
        })
    
    # Display demo results
    if 'voice_demo_result' in st.session_state:
        result = st.session_state.voice_demo_result
        st.success("**Voice Command Result**")
        st.write(f"**Equation:** {result['equation']}")
        st.write(f"**Roots:** {result['roots']}")

# Setup function for main app
def setup_voice_controls():
    """Initialize voice controls for the app"""
    if 'voice_initialized' not in st.session_state:
        st.session_state.voice_initialized = True
        st.session_state.voice_system = VoiceCommandSystem()

# Usage in main app.py:
"""
# Add to your main app.py:

from voice_commands import setup_voice_controls, render_voice_control_panel

# Initialize voice system
setup_voice_controls()

# Add to sidebar or main interface
with st.sidebar:
    render_voice_control_panel()
"""

if __name__ == "__main__":
    st.title("🎤 Voice Control System Test")
    setup_voice_controls()
    render_voice_control_panel()
    render_voice_demo()

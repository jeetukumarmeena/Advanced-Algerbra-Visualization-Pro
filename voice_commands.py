import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import re
import json
from datetime import datetime
import numpy as np
from math_engine import math_engine
from visualizations import viz
import tempfile
import os

class VoiceCommandSystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = None
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.last_command_time = 0
        self.command_cooldown = 2  # seconds
        self.audio_data_queue = queue.Queue()
        self.setup_voice_engine()
        
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
            "calculate integral": "calculate_integral",
            "graph function": "graph_function",
            
            # Control commands
            "stop listening": "stop_listening",
            "start listening": "start_listening",
            "help": "show_help",
            "clear screen": "clear_screen",
            "what can I say": "show_commands",
            
            # Learning commands
            "explain concept": "explain_concept",
            "show example": "show_example",
            "generate problem": "generate_problem",
            "check solution": "check_solution"
        }
        
        # Math keywords for natural language processing
        self.math_keywords = {
            'quadratic': 'quadratic',
            'polynomial': 'polynomial',
            'equation': 'equation',
            'solve': 'solve',
            'expand': 'expand',
            'factor': 'factor',
            'derivative': 'derivative',
            'integral': 'integral',
            'graph': 'graph',
            'plot': 'graph',
            'calculate': 'calculate',
            'simplify': 'simplify'
        }
        
        # Parameter patterns for natural language parsing
        self.parameter_patterns = {
            'coefficient': r'(\-?\d+(?:\.\d+)?)',
            'variable': r'[a-zA-Z]',
            'expression': r'([a-zA-Z0-9\+\-\*\/\^\(\) ]+)'
        }

    def setup_voice_engine(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            # Configure voice properties
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)  # First available voice
            self.tts_engine.setProperty('rate', 150)  # Speech rate
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
        except Exception as e:
            st.warning(f"Text-to-speech not available: {e}")

    def speak(self, text):
        """Convert text to speech"""
        if self.tts_engine:
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
        else:
            # Fallback: show text in Streamlit
            st.info(f"🔊 {text}")

    def listen(self, timeout=5):
        """Listen for voice input and return recognized text"""
        try:
            with self.microphone as source:
                st.info("🎤 Listening... Speak now!")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            st.success(f"🎤 Heard: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            st.warning("⏰ Listening timeout")
            return None
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            st.error(f"🚫 Speech recognition error: {e}")
            return None

    def process_command(self, command_text):
        """Process voice command and return action"""
        if not command_text:
            return None
            
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return None
            
        self.last_command_time = current_time
        
        # Exact command matching
        normalized_command = command_text.lower().strip()
        if normalized_command in self.commands:
            return self.commands[normalized_command]
        
        # Fuzzy matching and natural language processing
        return self._parse_natural_language(command_text)

    def _parse_natural_language(self, text):
        """Parse natural language math commands"""
        text_lower = text.lower()
        
        # Check for math operations
        if any(keyword in text_lower for keyword in ['solve', 'calculate', 'find']):
            if 'quadratic' in text_lower or 'equation' in text_lower:
                return self._parse_quadratic_command(text)
            elif 'derivative' in text_lower:
                return self._parse_derivative_command(text)
            elif 'integral' in text_lower:
                return self._parse_integral_command(text)
                
        elif 'expand' in text_lower:
            return self._parse_expansion_command(text)
            
        elif 'factor' in text_lower:
            return self._parse_factor_command(text)
            
        elif any(keyword in text_lower for keyword in ['graph', 'plot']):
            return self._parse_graph_command(text)
            
        elif 'help' in text_lower or 'what can' in text_lower:
            return "show_commands"
            
        return None

    def _parse_quadratic_command(self, text):
        """Parse quadratic equation from voice command"""
        try:
            # Look for coefficients in the text
            numbers = re.findall(r'-?\d+\.?\d*', text)
            if len(numbers) >= 3:
                a, b, c = map(float, numbers[:3])
                return {
                    'action': 'solve_quadratic_voice',
                    'parameters': {'a': a, 'b': b, 'c': c}
                }
            else:
                # Try to extract using common patterns
                patterns = [
                    r'(\d+)x squared[^\d]*(\d+)x[^\d]*(\d+)',
                    r'(\d+)x\^2[^\d]*(\d+)x[^\d]*(\d+)',
                    r'a[^\d]*(\d+)[^\d]*b[^\d]*(\d+)[^\d]*c[^\d]*(\d+)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text.lower())
                    if match:
                        a, b, c = map(float, match.groups())
                        return {
                            'action': 'solve_quadratic_voice',
                            'parameters': {'a': a, 'b': b, 'c': c}
                        }
                        
        except Exception as e:
            st.error(f"Error parsing quadratic command: {e}")
            
        return {'action': 'solve_quadratic', 'parameters': {}}

    def _parse_derivative_command(self, text):
        """Parse derivative command from voice"""
        try:
            # Look for mathematical expressions
            if 'of' in text:
                expression_part = text.split('of')[-1].strip()
                # Simple variable detection
                variable = 'x'
                if 'with respect to' in expression_part:
                    parts = expression_part.split('with respect to')
                    expression_part = parts[0].strip()
                    var_match = re.search(r'[a-zA-Z]', parts[1])
                    if var_match:
                        variable = var_match.group()
                
                return {
                    'action': 'calculate_derivative_voice',
                    'parameters': {'expression': expression_part, 'variable': variable}
                }
        except Exception as e:
            st.error(f"Error parsing derivative command: {e}")
            
        return {'action': 'calculate_derivative', 'parameters': {}}

    def _parse_integral_command(self, text):
        """Parse integral command from voice"""
        return {'action': 'calculate_integral', 'parameters': {}}

    def _parse_expansion_command(self, text):
        """Parse expansion command from voice"""
        return {'action': 'expand_expression', 'parameters': {}}

    def _parse_factor_command(self, text):
        """Parse factor command from voice"""
        return {'action': 'factor_expression', 'parameters': {}}

    def _parse_graph_command(self, text):
        """Parse graph command from voice"""
        return {'action': 'graph_function', 'parameters': {}}

    def execute_command(self, command_data):
        """Execute the voice command"""
        if not command_data:
            return
            
        action = command_data.get('action')
        parameters = command_data.get('parameters', {})
        
        st.info(f"🎯 Executing: {action}")
        
        # Navigation commands
        if action == "navigate_dashboard":
            st.session_state.current_section = "Dashboard"
            self.speak("Navigating to dashboard")
            
        elif action == "navigate_quadratic":
            st.session_state.current_section = "Quadratic Solver"
            self.speak("Opening quadratic equation solver")
            
        elif action == "navigate_polynomial":
            st.session_state.current_section = "Polynomial Analyzer"
            self.speak("Opening polynomial analyzer")
            
        elif action == "navigate_identities":
            st.session_state.current_section = "Identities"
            self.speak("Showing algebraic identities")
            
        elif action == "navigate_practice":
            st.session_state.current_section = "Practice"
            self.speak("Opening practice problems")
            
        elif action == "navigate_progress":
            st.session_state.current_section = "Progress"
            self.speak("Showing your progress")
            
        # Math operation commands
        elif action == "solve_quadratic_voice":
            self._execute_quadratic_solve(parameters)
            
        elif action == "solve_quadratic":
            st.session_state.current_section = "Quadratic Solver"
            self.speak("Please enter the coefficients for the quadratic equation")
            
        elif action == "calculate_derivative_voice":
            self._execute_derivative_calculation(parameters)
            
        elif action == "calculate_derivative":
            st.session_state.current_section = "Calculus"
            self.speak("Please specify the function to differentiate")
            
        elif action == "calculate_integral":
            st.session_state.current_section = "Calculus"
            self.speak("Please specify the function to integrate")
            
        elif action == "expand_expression":
            st.session_state.current_section = "Identities"
            self.speak("Please specify the expression to expand")
            
        elif action == "factor_expression":
            st.session_state.current_section = "Identities"
            self.speak("Please specify the expression to factor")
            
        elif action == "graph_function":
            st.session_state.current_section = "Graphing"
            self.speak("Please specify the function to graph")
            
        # Control commands
        elif action == "stop_listening":
            self.is_listening = False
            self.speak("Voice commands disabled")
            
        elif action == "start_listening":
            self.is_listening = True
            self.speak("Voice commands enabled")
            
        elif action == "show_help":
            self._show_voice_help()
            
        elif action == "show_commands":
            self._show_available_commands()
            
        elif action == "clear_screen":
            st.session_state.clear()
            self.speak("Screen cleared")
            
        # Learning commands
        elif action == "explain_concept":
            self.speak("Which concept would you like me to explain?")
            
        elif action == "show_example":
            self.speak("Which concept would you like an example for?")
            
        elif action == "generate_problem":
            self._generate_random_problem()
            
        elif action == "check_solution":
            self.speak("Please provide the problem and your solution")
            
        else:
            self.speak("Command not recognized. Say 'help' for available commands.")

    def _execute_quadratic_solve(self, parameters):
        """Execute quadratic equation solving with voice parameters"""
        a = parameters.get('a', 1)
        b = parameters.get('b', 0)
        c = parameters.get('c', 0)
        
        try:
            # Solve the equation
            solution = math_engine.solve_quadratic(a, b, c)
            
            # Store in session state for display
            st.session_state.voice_quadratic_result = {
                'equation': f"{a}x² + {b}x + {c} = 0",
                'solution': solution
            }
            
            # Speak the result
            if solution["type"] == "real":
                root1, root2 = solution["roots"]
                response = f"The roots are {root1:.2f} and {root2:.2f}"
            elif solution["type"] == "double":
                root = solution["roots"][0]
                response = f"The equation has a double root at {root:.2f}"
            else:
                real_part, imag_part = solution["roots"]
                response = f"The roots are complex: {real_part:.2f} plus or minus {imag_part:.2f} i"
                
            self.speak(response)
            st.session_state.current_section = "Quadratic Solver"
            
        except Exception as e:
            error_msg = f"Error solving equation: {e}"
            self.speak(error_msg)
            st.error(error_msg)

    def _execute_derivative_calculation(self, parameters):
        """Execute derivative calculation with voice parameters"""
        expression = parameters.get('expression', 'x^2')
        variable = parameters.get('variable', 'x')
        
        try:
            # Clean up the expression
            expression = expression.replace(' squared', '^2').replace(' cube', '^3')
            
            # Calculate derivative
            result = math_engine.calculate_derivative(expression, variable)
            
            if result["success"]:
                st.session_state.voice_derivative_result = result
                response = f"The derivative of {expression} is {result['derivative']}"
                self.speak(response)
            else:
                self.speak("Sorry, I couldn't calculate that derivative")
                
        except Exception as e:
            self.speak(f"Error calculating derivative: {e}")

    def _show_voice_help(self):
        """Show voice command help"""
        help_text = """
        **Voice Command Help:**
        
        **Navigation:**
        - "Go to dashboard" - Main dashboard
        - "Show quadratic solver" - Quadratic equations
        - "Open polynomial analyzer" - Polynomial analysis
        - "Show identities" - Algebraic identities
        - "Practice problems" - Practice mode
        - "Show progress" - Progress tracking
        
        **Math Operations:**
        - "Solve quadratic" - Solve quadratic equations
        - "Expand expression" - Expand algebraic expressions  
        - "Factor expression" - Factor expressions
        - "Calculate derivative" - Find derivatives
        - "Calculate integral" - Find integrals
        - "Graph function" - Plot functions
        
        **Control:**
        - "Stop listening" - Disable voice commands
        - "Start listening" - Enable voice commands
        - "Help" - Show this help
        - "Clear screen" - Clear the interface
        - "What can I say" - List available commands
        """
        
        st.info(help_text)
        self.speak("Voice help displayed on screen. You can say commands like solve quadratic, expand expression, or show progress.")

    def _show_available_commands(self):
        """List all available voice commands"""
        categories = {}
        for cmd, action in self.commands.items():
            category = action.split('_')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        
        command_list = "**Available Voice Commands:**\n\n"
        for category, cmds in categories.items():
            command_list += f"**{category.title()}:**\n"
            for cmd in cmds:
                command_list += f"- '{cmd}'\n"
            command_list += "\n"
        
        st.info(command_list)
        self.speak("Available commands displayed on screen.")

    def _generate_random_problem(self):
        """Generate a random math problem"""
        import random
        problem_types = [
            "quadratic equation",
            "polynomial expansion", 
            "factoring problem",
            "derivative calculation"
        ]
        
        problem_type = random.choice(problem_types)
        self.speak(f"Here's a random {problem_type} to solve")
        
        # Store problem in session state
        st.session_state.voice_generated_problem = {
            'type': problem_type,
            'text': f"Practice {problem_type}",
            'difficulty': 'medium'
        }

    def start_voice_listener(self):
        """Start continuous voice listening in background"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.speak("Voice commands activated. Say 'help' for available commands.")
        
        def _listen_loop():
            while self.is_listening:
                try:
                    command_text = self.listen(timeout=10)
                    if command_text:
                        command_data = self.process_command(command_text)
                        if command_data:
                            # Use callback to update Streamlit
                            if hasattr(st, 'callback'):
                                st.callback(lambda: self.execute_command(command_data))()
                            else:
                                # Fallback: store command for main thread to execute
                                st.session_state.pending_voice_command = command_data
                                
                except Exception as e:
                    if self.is_listening:  # Only log if we're still supposed to be listening
                        st.error(f"Voice listener error: {e}")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
        # Start listening thread
        listener_thread = threading.Thread(target=_listen_loop)
        listener_thread.daemon = True
        listener_thread.start()

    def stop_voice_listener(self):
        """Stop voice listening"""
        self.is_listening = False
        self.speak("Voice commands deactivated")

# Streamlit UI Components for Voice Control
def render_voice_control_panel():
    """Render voice control interface in Streamlit"""
    st.markdown("---")
    st.header("🎤 Voice Control")
    
    # Initialize voice system in session state
    if 'voice_system' not in st.session_state:
        st.session_state.voice_system = VoiceCommandSystem()
    
    voice_system = st.session_state.voice_system
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎤 Start Listening", use_container_width=True):
            voice_system.start_voice_listener()
            st.success("Voice control activated!")
            
    with col2:
        if st.button("⏹️ Stop Listening", use_container_width=True):
            voice_system.stop_voice_listener()
            st.info("Voice control deactivated")
            
    with col3:
        if st.button("❓ Voice Help", use_container_width=True):
            voice_system._show_voice_help()
    
    # Quick voice command buttons
    st.subheader("Quick Commands")
    quick_cols = st.columns(4)
    
    with quick_cols[0]:
        if st.button("Solve Quadratic", use_container_width=True):
            voice_system.execute_command({'action': 'solve_quadratic', 'parameters': {}})
    
    with quick_cols[1]:
        if st.button("Show Progress", use_container_width=True):
            voice_system.execute_command({'action': 'navigate_progress', 'parameters': {}})
    
    with quick_cols[2]:
        if st.button("Generate Problem", use_container_width=True):
            voice_system.execute_command({'action': 'generate_problem', 'parameters': {}})
    
    with quick_cols[3]:
        if st.button("Clear Screen", use_container_width=True):
            voice_system.execute_command({'action': 'clear_screen', 'parameters': {}})
    
    # Voice command history
    if 'voice_command_history' not in st.session_state:
        st.session_state.voice_command_history = []
    
    if st.session_state.voice_command_history:
        st.subheader("Recent Commands")
        for i, cmd in enumerate(st.session_state.voice_command_history[-5:]):
            st.write(f"{i+1}. {cmd}")
    
    # Manual command input (for testing)
    st.subheader("Manual Command Input")
    manual_command = st.text_input("Or type a voice command:")
    if st.button("Execute Typed Command"):
        if manual_command:
            command_data = voice_system.process_command(manual_command)
            if command_data:
                voice_system.execute_command(command_data)
                st.session_state.voice_command_history.append(manual_command)
            else:
                st.error("Command not recognized")

def render_voice_command_demo():
    """Render a demo section for voice commands"""
    st.header("🎤 Voice Command Demo")
    
    st.info("""
    **Try these voice commands:**
    
    - **"Solve quadratic"** - Opens quadratic solver
    - **"Show progress"** - Shows your learning progress  
    - **"Generate problem"** - Creates a practice problem
    - **"What can I say"** - Lists all commands
    - **"Help"** - Shows voice command help
    """)
    
    # Demo of voice-based quadratic solver
    if st.button("🎯 Demo: Voice Quadratic Solver"):
        # Simulate voice command for quadratic solving
        demo_params = {'a': 1, 'b': -3, 'c': 2}
        voice_system = st.session_state.get('voice_system', VoiceCommandSystem())
        voice_system.execute_command({
            'action': 'solve_quadratic_voice',
            'parameters': demo_params
        })
    
    # Display voice command results
    if 'voice_quadratic_result' in st.session_state:
        result = st.session_state.voice_quadratic_result
        st.success(f"**Voice Solution:** {result['equation']}")
        st.write("**Result:**", result['solution'])
    
    if 'voice_derivative_result' in st.session_state:
        result = st.session_state.voice_derivative_result
        st.success("**Voice Derivative Calculation**")
        st.latex(f"\\frac{{d}}{{dx}}({result['function']}) = {result['derivative']}")

# Voice-based problem solver component
def voice_math_assistant():
    """Interactive voice-based math assistant"""
    st.header("🧮 Voice Math Assistant")
    
    if 'voice_system' not in st.session_state:
        st.session_state.voice_system = VoiceCommandSystem()
    
    voice_system = st.session_state.voice_system
    
    # Assistant status
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        status = "🟢 Active" if voice_system.is_listening else "🔴 Inactive"
        st.metric("Voice Assistant Status", status)
    
    with status_col2:
        if voice_system.is_listening:
            st.button("🔇 Mute Assistant", on_click=voice_system.stop_voice_listener)
        else:
            st.button("🔊 Activate Assistant", on_click=voice_system.start_voice_listener)
    
    # Interactive voice session
    st.subheader("Interactive Session")
    
    if st.button("🎤 Ask Math Question", key="ask_math"):
        with st.spinner("Listening for your question..."):
            question = voice_system.listen(timeout=10)
            if question:
                st.success(f"**Your question:** {question}")
                # Process the math question
                response = process_math_question(question, voice_system)
                st.info(f"**Assistant:** {response}")
                voice_system.speak(response)

def process_math_question(question, voice_system):
    """Process natural language math questions"""
    question_lower = question.lower()
    
    # Quadratic equations
    if any(word in question_lower for word in ['quadratic', 'equation', 'solve']):
        return "I can help you solve quadratic equations. Say 'solve quadratic' or go to the quadratic solver section."
    
    # Derivatives
    elif any(word in question_lower for word in ['derivative', 'differentiate']):
        return "I can calculate derivatives. Say 'calculate derivative' or specify a function to differentiate."
    
    # Integrals
    elif any(word in question_lower for word in ['integral', 'integrate']):
        return "I can calculate integrals. Say 'calculate integral' or specify a function to integrate."
    
    # Graphing
    elif any(word in question_lower for word in ['graph', 'plot']):
        return "I can graph functions. Say 'graph function' or specify what you'd like to plot."
    
    # General math help
    elif any(word in question_lower for word in ['help', 'how to', 'what is']):
        return "I can help with algebra, calculus, graphing, and more. Say 'help' for a list of commands or be specific about what you need."
    
    # Default response
    else:
        return "I understand you're asking about math. Please be more specific about what you'd like me to solve, calculate, or explain."

# Main voice control integration
def setup_voice_controls():
    """Set up voice controls for the main application"""
    if 'voice_initialized' not in st.session_state:
        st.session_state.voice_initialized = True
        st.session_state.voice_system = VoiceCommandSystem()
        
        # Initialize voice command history
        if 'voice_command_history' not in st.session_state:
            st.session_state.voice_command_history = []

# Global voice system instance
voice_system = VoiceCommandSystem()

# Example usage in main app
"""
# In your main app.py, add:

from voice_commands import setup_voice_controls, render_voice_control_panel

# Setup voice controls
setup_voice_controls()

# Add voice control panel to sidebar or main interface
render_voice_control_panel()

# Or add voice assistant to a specific section
voice_math_assistant()
"""

if __name__ == "__main__":
    # Test the voice system
    st.title("🎤 Voice Commands Test")
    
    render_voice_control_panel()
    render_voice_command_demo()
    voice_math_assistant()
    
    # Test individual components
    if st.button("Test Voice Recognition"):
        voice_system = VoiceCommandSystem()
        text = voice_system.listen()
        if text:
            st.success(f"Recognized: {text}")
            command = voice_system.process_command(text)
            st.info(f"Command: {command}")
        else:
            st.error("No speech detected")
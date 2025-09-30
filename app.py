import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import random

# Safe imports with error handling
try:
    from math_engine import math_engine
    MATH_ENGINE_AVAILABLE = True
except ImportError as e:
    MATH_ENGINE_AVAILABLE = False
    st.error(f"Math engine not available: {e}")

try:
    from visualizations import viz
    VISUALIZATIONS_AVAILABLE = True
except ImportError:
    VISUALIZATIONS_AVAILABLE = False

try:
    from gamification import game_engine
    GAMIFICATION_AVAILABLE = True
except ImportError:
    GAMIFICATION_AVAILABLE = False

try:
    from theme import get_theme_css, THEMES
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False

try:
    from auth import AuthSystem, render_login_register_forms, initialize_auth
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

try:
    from voice_commands import VoiceCommandSystem, render_voice_control_panel
    VOICE_AVAILABLE = True
except ImportError as e:
    VOICE_AVAILABLE = False
    st.warning(f"Voice features disabled: {e}")

# Configuration with fallbacks
class Config:
    def __init__(self):
        self.APP_NAME = "Advanced Algebra Visualizer"
        self.DEFAULT_THEME = "light"
        self.ENABLE_GAMIFICATION = True

config = Config()

# Page configuration
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AlgebraVisualizerApp:
    def __init__(self):
        self.setup_session_state()
        if AUTH_AVAILABLE:
            self.auth = AuthSystem()
        if VOICE_AVAILABLE:
            self.voice_system = VoiceCommandSystem()
    
    def setup_session_state(self):
        """Initialize session state variables"""
        default_states = {
            'current_section': "Dashboard",
            'user_id': f"user_{int(time.time())}",
            'theme': config.DEFAULT_THEME,
            'learning_mode': "Intermediate",
            'random_problem': None,
            'is_authenticated': False,
            'show_auth': False
        }
        
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render_sidebar(self):
        """Render the sidebar with controls"""
        with st.sidebar:
            st.title("🎨 Control Panel")
            
            # Authentication Section
            if AUTH_AVAILABLE:
                if not st.session_state.is_authenticated:
                    st.subheader("🔐 Authentication")
                    if st.button("Login / Register", use_container_width=True):
                        st.session_state.show_auth = True
                else:
                    user_data = self.auth.get_current_user()
                    if user_data:
                        st.subheader(f"👤 {user_data['username']}")
                        st.write(f"Level: {user_data.get('level', 'Beginner')}")
                        if st.button("Logout", use_container_width=True):
                            self.auth.logout_user()
                            st.session_state.is_authenticated = False
                            st.rerun()
            else:
                st.info("🔐 Authentication unavailable")
            
            # Theme Selection
            if THEME_AVAILABLE:
                st.subheader("🎨 Theme Settings")
                theme = st.selectbox(
                    "Choose Theme:",
                    list(THEMES.keys()),
                    index=list(THEMES.keys()).index(st.session_state.theme),
                    key="theme_selector"
                )
                
                if theme != st.session_state.theme:
                    st.session_state.theme = theme
                    st.rerun()
            else:
                st.session_state.theme = "light"
            
            # Learning Mode
            st.subheader("📚 Learning Mode")
            st.session_state.learning_mode = st.selectbox(
                "Select Difficulty:",
                ["Beginner", "Intermediate", "Advanced", "Expert"],
                index=1
            )
            
            # Concept Selection
            st.subheader("🎯 Focus Concepts")
            concepts = st.multiselect(
                "Select concepts to practice:",
                ["Quadratic Equations", "Polynomials", "Factorization", "Exponents", 
                 "Algebraic Identities", "Word Problems", "Graphical Analysis", "3D Visualization"],
                default=["Quadratic Equations", "Algebraic Identities"]
            )
            
            # Problem Generator
            st.subheader("🔢 Problem Generator")
            if st.button("🎲 Generate Random Problem", use_container_width=True):
                st.session_state.random_problem = self.generate_random_problem(
                    st.session_state.learning_mode
                )
            
            # Voice Control
            if VOICE_AVAILABLE:
                st.subheader("🎤 Voice Control")
                if st.button("Start Voice Commands", use_container_width=True):
                    self.voice_system.start_voice_listener()
                    st.success("Voice commands activated!")
            else:
                st.subheader("🎤 Voice Control")
                st.info("Voice features unavailable")
            
            # User Progress
            if GAMIFICATION_AVAILABLE and st.session_state.is_authenticated:
                self.render_progress_section()
    
    def render_progress_section(self):
        """Render user progress in sidebar"""
        st.subheader("📊 Your Progress")
        
        user_data = game_engine.get_user_data(st.session_state.user_id)
        
        if user_data:
            # Simple progress display
            current_level = user_data.get("current_level", 1)
            current_points = user_data.get("total_points", 0)
            problems_solved = user_data.get("problems_solved", 0)
            streak_days = user_data.get("streak_days", 0)
            
            st.write(f"**Level:** {current_level}")
            st.write(f"**Points:** {current_points}")
            st.write(f"**Problems Solved:** {problems_solved}")
            
            if streak_days > 0:
                st.info(f"🔥 {streak_days} day streak!")
        else:
            st.info("Start solving problems to track your progress!")
    
    def generate_random_problem(self, level):
        """Generate random algebra problems based on level"""
        problems = {
            "Beginner": [
                "Solve: (x + 3)(x - 2) = 0",
                "Expand: (2x + 1)²",
                "Factor: x² - 9",
                "Simplify: (3x² + 2x) - (x² - 4x)",
                "Solve: 2x + 5 = 13"
            ],
            "Intermediate": [
                "Solve the system: 2x + 3y = 7, x - y = 1",
                "Factor completely: x³ - 8",
                "Find roots: 2x² - 5x + 2 = 0",
                "Simplify: (x² - 4)/(x - 2)",
                "Solve: |2x - 3| = 5"
            ],
            "Advanced": [
                "Solve: x⁴ - 5x² + 4 = 0",
                "Expand: (x + y + z)²",
                "Factor: x³ + y³ + z³ - 3xyz",
                "Find domain: √(x² - 4)",
                "Solve: 3ˣ = 81"
            ],
            "Expert": [
                "Solve: |x² - 4| = 3",
                "Prove: (a + b + c)² = a² + b² + c² + 2ab + 2bc + 2ca",
                "Find all real solutions: x³ - 3x + 1 = 0",
                "Simplify: (aⁿ - bⁿ)/(a - b)",
                "Solve: log₂(x) + log₂(x - 2) = 3"
            ]
        }
        return random.choice(problems.get(level, problems["Intermediate"]))
    
    def render_main_dashboard(self):
        """Main dashboard with overview"""
        st.markdown('<div class="section-header">📊 Algebra Learning Dashboard</div>', unsafe_allow_html=True)
        
        # Welcome message
        if st.session_state.is_authenticated and AUTH_AVAILABLE:
            user_data = self.auth.get_current_user()
            if user_data:
                st.success(f"🎉 Welcome back, {user_data['username']}! Ready to learn some algebra?")
        else:
            st.success("🎉 Welcome to Advanced Algebra Visualizer! Ready to learn some algebra?")
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Formulas Available", "26+")
        with col2:
            st.metric("Interactive Tools", "8")
        with col3:
            st.metric("Visualizations", "15+")
        with col4:
            st.metric("Practice Problems", "50+")
        
        # Quick access cards
        st.subheader("🚀 Quick Access")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Quadratic Solver", use_container_width=True, key="quick_quad"):
                st.session_state.current_section = "Quadratic Solver"
                st.rerun()
        with col2:
            if st.button("📈 Polynomial Analyzer", use_container_width=True, key="quick_poly"):
                st.session_state.current_section = "Polynomial Analyzer"
                st.rerun()
        with col3:
            if st.button("🔬 Identity Prover", use_container_width=True, key="quick_id"):
                st.session_state.current_section = "Identity Prover"
                st.rerun()
        with col4:
            if st.button("🌍 Real World Apps", use_container_width=True, key="quick_real"):
                st.session_state.current_section = "Real World"
                st.rerun()
        
        # Voice Control Section
        if VOICE_AVAILABLE:
            st.markdown("---")
            st.subheader("🎤 Voice Control")
            render_voice_control_panel()
        else:
            st.markdown("---")
            st.subheader("🎤 Voice Control")
            st.info("Voice commands are currently unavailable in this environment.")
        
        # Random problem challenge
        if st.session_state.random_problem:
            st.markdown("---")
            st.subheader("🎲 Daily Challenge")
            st.info(f"**Problem:** {st.session_state.random_problem}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                user_solution = st.text_input("Your solution:")
            with col2:
                if st.button("Check Solution", use_container_width=True):
                    if user_solution:
                        st.success("Solution submitted! 🎉")
                        if GAMIFICATION_AVAILABLE and st.session_state.is_authenticated:
                            try:
                                user_data, points = game_engine.update_user_progress(
                                    st.session_state.user_id, "Random Problem", 2, True
                                )
                                st.success(f"🎉 +{points} points earned!")
                            except Exception as e:
                                st.error(f"Error updating progress: {e}")
                    else:
                        st.warning("Please enter your solution first")
    
    def render_quadratic_solver(self):
        """Advanced quadratic equation solver"""
        st.markdown('<div class="section-header">🎯 Advanced Quadratic Equation Solver</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="problem-solver">', unsafe_allow_html=True)
            st.subheader("🔍 Input Your Equation")
            
            equation_type = st.radio(
                "Equation Format:",
                ["Standard Form: ax² + bx + c = 0", "Vertex Form: a(x-h)² + k", "Factored Form: a(x-r₁)(x-r₂)"],
                horizontal=True
            )
            
            if equation_type == "Standard Form: ax² + bx + c = 0":
                a = st.slider("a coefficient", -10.0, 10.0, 1.0, 0.1, key="quad_a")
                b = st.slider("b coefficient", -10.0, 10.0, -3.0, 0.1, key="quad_b")
                c = st.slider("c constant", -10.0, 10.0, 2.0, 0.1, key="quad_c")
                equation = f"{a}x² + {b}x + {c} = 0"
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Real-time solution
            if MATH_ENGINE_AVAILABLE:
                st.markdown('<div class="step-by-step">', unsafe_allow_html=True)
                st.subheader("📝 Step-by-Step Solution")
                
                solution = math_engine.solve_quadratic(a, b, c)
                
                st.write(f"**Step 1:** Calculate discriminant")
                st.latex(f"D = b^2 - 4ac = ({b})^2 - 4({a})({c}) = {solution['discriminant']}")
                
                if solution["type"] == "real":
                    st.write("**Step 2:** Two real roots")
                    root1, root2 = solution["roots"]
                    st.latex(f"x = \\frac{{-b \\pm \\sqrt{{D}}}}{{2a}}")
                    st.latex(f"x_1 = {root1:.4f}, \\quad x_2 = {root2:.4f}")
                elif solution["type"] == "double":
                    st.write("**Step 2:** One real root (double root)")
                    root = solution["roots"][0]
                    st.latex(f"x = \\frac{{-b}}{{2a}} = {root:.4f}")
                else:
                    st.write("**Step 2:** Two complex roots")
                    real_part, imag_part = solution["roots"]
                    st.latex(f"x = {real_part:.4f} \\pm {imag_part:.4f}i")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Math engine unavailable for step-by-step solutions")
        
        with col2:
            # Visualization
            st.subheader("📊 Graphical Analysis")
            try:
                # Create simple plot directly
                x = np.linspace(-10, 10, 400)
                y = a*x**2 + b*x + c
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'{a}x² + {b}x + {c}'))
                
                # Add roots if available
                if MATH_ENGINE_AVAILABLE:
                    solution = math_engine.solve_quadratic(a, b, c)
                    if solution["type"] == "real":
                        root1, root2 = solution["roots"]
                        fig.add_trace(go.Scatter(x=[root1, root2], y=[0, 0], 
                                               mode='markers', marker=dict(size=10, color='red'),
                                               name='Roots'))
                
                fig.update_layout(title="Quadratic Function", xaxis_title="x", yaxis_title="y")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not generate graph: {e}")
            
            # Additional analysis
            col1, col2, col3 = st.columns(3)
            with col1:
                discriminant = b**2 - 4*a*c
                st.metric("Discriminant", f"{discriminant:.2f}")
            with col2:
                vertex_x = -b/(2*a)
                vertex_y = a*vertex_x**2 + b*vertex_x + c
                st.metric("Vertex", f"({vertex_x:.2f}, {vertex_y:.2f})")
            with col3:
                axis_symmetry = f"x = {vertex_x:.2f}"
                st.metric("Axis of Symmetry", axis_symmetry)
            
            # Practice problem
            if st.button("🎯 Practice Similar Problem"):
                new_a = random.choice([1, 2, -1, -2])
                new_b = random.randint(-5, 5)
                new_c = random.randint(-5, 5)
                st.info(f"Try solving: {new_a}x² + {new_b}x + {new_c} = 0")

            if GAMIFICATION_AVAILABLE and st.session_state.is_authenticated:
                try:
                    user_data, points = game_engine.update_user_progress(
                        str(st.session_state.user_id), "Quadratic Equations", 2, True
                    )
                    st.success(f"🎉 +{points} points earned!")
                except Exception as e:
                    st.error(f"Error updating progress: {e}")

    def render_polynomial_analyzer(self):
        """Polynomial analysis section"""
        st.markdown('<div class="section-header">📈 Polynomial Analyzer</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎛️ Polynomial Input")
            degree = st.slider("Polynomial Degree", 1, 6, 3, key="poly_degree")
            
            coefficients = []
            st.write("Enter coefficients (from highest degree to constant):")
            cols = st.columns(degree + 1)
            for i in range(degree, -1, -1):
                with cols[degree - i]:
                    if i == degree:
                        coeff = st.number_input(f"x^{i}", value=1.0, key=f"coeff_{i}")
                    else:
                        coeff = st.number_input(f"x^{i}", value=0.0, key=f"coeff_{i}")
                    coefficients.append(coeff)
            
            # Display polynomial
            poly_str = "P(x) = "
            terms = []
            for i, coeff in enumerate(coefficients):
                power = degree - i
                if coeff != 0:
                    if power == 0:
                        terms.append(f"{coeff}")
                    elif power == 1:
                        terms.append(f"{coeff}x")
                    else:
                        terms.append(f"{coeff}x^{power}")
            poly_str += " + ".join(terms) if terms else "0"
            st.success(f"**Polynomial:** {poly_str}")
            
            # Analyze polynomial
            if MATH_ENGINE_AVAILABLE and st.button("Analyze Polynomial"):
                solution = math_engine.solve_polynomial(coefficients)
                
                if solution["success"]:
                    st.subheader("🔍 Analysis Results")
                    
                    if solution["real_roots"]:
                        st.write("**Real Roots:**")
                        for i, root in enumerate(solution["real_roots"], 1):
                            st.write(f"x_{i} = {root.real:.4f}")
                    
                    if solution["complex_roots"]:
                        st.write("**Complex Roots:**")
                        for i, root in enumerate(solution["complex_roots"], 1):
                            st.write(f"x_{i} = {root.real:.4f} ± {abs(root.imag):.4f}i")
                else:
                    st.error("Could not analyze polynomial")
        
        with col2:
            st.subheader("📊 Polynomial Graph")
            
            # Create plot
            x = np.linspace(-5, 5, 400)
            y = np.polyval(coefficients, x)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Polynomial',
                                   line=dict(width=3, color="#704FD1")))
            
            # Add roots if available
            if MATH_ENGINE_AVAILABLE:
                try:
                    solution = math_engine.solve_polynomial(coefficients)
                    if solution["success"] and solution["real_roots"]:
                        real_roots = [r.real for r in solution["real_roots"]]
                        fig.add_trace(go.Scatter(x=real_roots, 
                                               y=np.zeros(len(real_roots)),
                                               mode='markers', 
                                               marker=dict(size=10, color='red'),
                                               name='Real Roots'))
                except:
                    pass
            
            fig.update_layout(
                title="Polynomial Graph",
                xaxis_title="x",
                yaxis_title="P(x)",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_identity_prover(self):
        """Interactive identity prover section"""
        st.markdown('<div class="section-header">🔬 Interactive Identity Prover</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🎯 Choose Identity")
            identity = st.selectbox(
                "Select Identity:",
                [
                    "(a + b)² = a² + 2ab + b²",
                    "(a - b)² = a² - 2ab + b²", 
                    "a² - b² = (a - b)(a + b)",
                    "(a + b)³ = a³ + 3a²b + 3ab² + b³",
                    "a³ + b³ = (a + b)(a² - ab + b²)",
                    "a³ - b³ = (a - b)(a² + ab + b²)"
                ]
            )
            
            a_val = st.slider("Value of a", 1, 10, 4, key="proof_a")
            b_val = st.slider("Value of b", 1, 10, 3, key="proof_b")
            
            # Define expressions for evaluation
            if identity == "(a + b)² = a² + 2ab + b²":
                left_side = (a_val + b_val) ** 2
                right_side = a_val**2 + 2*a_val*b_val + b_val**2
                left_expr = f"({a_val} + {b_val})²"
                right_expr = f"{a_val}² + 2×{a_val}×{b_val} + {b_val}²"
                
            elif identity == "(a - b)² = a² - 2ab + b²":
                left_side = (a_val - b_val) ** 2
                right_side = a_val**2 - 2*a_val*b_val + b_val**2
                left_expr = f"({a_val} - {b_val})²"
                right_expr = f"{a_val}² - 2×{a_val}×{b_val} + {b_val}²"
                
            elif identity == "a² - b² = (a - b)(a + b)":
                left_side = a_val**2 - b_val**2
                right_side = (a_val - b_val) * (a_val + b_val)
                left_expr = f"{a_val}² - {b_val}²"
                right_expr = f"({a_val} - {b_val})×({a_val} + {b_val})"
                
            elif identity == "(a + b)³ = a³ + 3a²b + 3ab² + b³":
                left_side = (a_val + b_val) ** 3
                right_side = a_val**3 + 3*a_val**2*b_val + 3*a_val*b_val**2 + b_val**3
                left_expr = f"({a_val} + {b_val})³"
                right_expr = f"{a_val}³ + 3×{a_val}²×{b_val} + 3×{a_val}×{b_val}² + {b_val}³"
                
            elif identity == "a³ + b³ = (a + b)(a² - ab + b²)":
                left_side = a_val**3 + b_val**3
                right_side = (a_val + b_val) * (a_val**2 - a_val*b_val + b_val**2)
                left_expr = f"{a_val}³ + {b_val}³"
                right_expr = f"({a_val} + {b_val})×({a_val}² - {a_val}×{b_val} + {b_val}²)"
                
            elif identity == "a³ - b³ = (a - b)(a² + ab + b²)":
                left_side = a_val**3 - b_val**3
                right_side = (a_val - b_val) * (a_val**2 + a_val*b_val + b_val**2)
                left_expr = f"{a_val}³ - {b_val}³"
                right_expr = f"({a_val} - {b_val})×({a_val}² + {a_val}×{b_val} + {b_val}²)"
            
            # Display the identity being tested
            st.info(f"**Testing:** {identity}")
            st.write(f"With a = {a_val}, b = {b_val}")
            
            # Prove identity
            if st.button("Prove Identity"):
                try:
                    is_identity = abs(left_side - right_side) < 1e-10  # Numerical verification
                    
                    if is_identity:
                        st.success("✅ Identity verified!")
                        st.latex(f"{left_expr} = {right_expr}")
                        
                        # Show numerical verification
                        st.write(f"**Numerical verification:**")
                        st.write(f"Left side: {left_expr} = {left_side}")
                        st.write(f"Right side: {right_expr} = {right_side}")
                        st.write(f"Both sides equal: {left_side == right_side}")
                    else:
                        st.error("❌ Not an identity")
                        st.latex(f"{left_expr} \\neq {right_expr}")
                except Exception as e:
                    st.error(f"❌ Error in calculation: {str(e)}")
        
        with col2:
            st.subheader("📖 Algebraic Proof")
            
            if identity == "(a + b)² = a² + 2ab + b²":
                st.write("**Step 1:** Start with (a + b)²")
                st.latex(r"(a + b)^2 = (a + b)(a + b)")
                
                st.write("**Step 2:** Apply distributive property")
                st.latex(r"= a(a + b) + b(a + b)")
                
                st.write("**Step 3:** Expand")
                st.latex(r"= a^2 + ab + ab + b^2")
                
                st.write("**Step 4:** Combine like terms")
                st.latex(r"= a^2 + 2ab + b^2")
                
                st.success("**Proof Complete!**")
            
            elif identity == "a² - b² = (a - b)(a + b)":
                st.write("**Step 1:** Start with (a - b)(a + b)")
                st.latex(r"(a - b)(a + b)")
                
                st.write("**Step 2:** Apply distributive property")
                st.latex(r"= a(a + b) - b(a + b)")
                
                st.write("**Step 3:** Expand")
                st.latex(r"= a^2 + ab - ab - b^2")
                
                st.write("**Step 4:** Combine like terms")
                st.latex(r"= a^2 - b^2")
                
                st.success("**Proof Complete!**")
            
            elif identity == "(a + b)³ = a³ + 3a²b + 3ab² + b³":
                st.write("**Step 1:** Start with (a + b)³")
                st.latex(r"(a + b)^3 = (a + b)(a + b)^2")
                
                st.write("**Step 2:** Expand (a + b)²")
                st.latex(r"= (a + b)(a^2 + 2ab + b^2)")
                
                st.write("**Step 3:** Apply distributive property")
                st.latex(r"= a(a^2 + 2ab + b^2) + b(a^2 + 2ab + b^2)")
                
                st.write("**Step 4:** Expand")
                st.latex(r"= a^3 + 2a^2b + ab^2 + a^2b + 2ab^2 + b^3")
                
                st.write("**Step 5:** Combine like terms")
                st.latex(r"= a^3 + 3a^2b + 3ab^2 + b^3")
                
                st.success("**Proof Complete!**")
            
            else:
                st.info("Select an identity to see the step-by-step algebraic proof")
    
    def render_real_world_apps(self):
        """Real-world applications section"""
        st.markdown('<div class="section-header">🌍 Real-World Applications</div>', unsafe_allow_html=True)
        
        app_type = st.selectbox(
            "Choose Application:",
            ["Projectile Motion", "Business Profit", "Geometry Problems", "Physics Applications"]
        )
        
        if app_type == "Projectile Motion":
            self.render_projectile_motion()
        elif app_type == "Business Profit":
            self.render_business_profit()
        elif app_type == "Geometry Problems":
            self.render_geometry_problems()
        else:
            self.render_physics_applications()
    
    def render_projectile_motion(self):
        """Projectile motion calculator"""
        st.subheader("🚀 Projectile Motion Calculator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            initial_velocity = st.slider("Initial Velocity (m/s)", 10, 100, 50)
            launch_angle = st.slider("Launch Angle (degrees)", 0, 90, 45)
            initial_height = st.slider("Initial Height (m)", 0, 100, 10)
        
        with col2:
            # Physics calculations
            g = 9.81
            angle_rad = np.radians(launch_angle)
            
            # Time of flight
            time_flight = (initial_velocity * np.sin(angle_rad) + 
                          np.sqrt((initial_velocity * np.sin(angle_rad))**2 + 2*g*initial_height)) / g
            
            # Maximum height
            max_height = initial_height + (initial_velocity * np.sin(angle_rad))**2 / (2*g)
            
            # Range
            range_val = initial_velocity * np.cos(angle_rad) * time_flight
            
            st.metric("Time of Flight", f"{time_flight:.2f} s")
            st.metric("Maximum Height", f"{max_height:.2f} m")
            st.metric("Range", f"{range_val:.2f} m")
        
        # Plot trajectory
        t = np.linspace(0, time_flight, 100)
        x = initial_velocity * np.cos(angle_rad) * t
        y = initial_height + initial_velocity * np.sin(angle_rad) * t - 0.5 * g * t**2
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Trajectory',
                               line=dict(width=4, color='#F56565')))
        fig.update_layout(
            title="Projectile Trajectory",
            xaxis_title="Distance (m)",
            yaxis_title="Height (m)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_business_profit(self):
        """Business profit optimization"""
        st.subheader("💰 Business Profit Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fixed_costs = st.number_input("Fixed Costs ($)", value=1000)
            variable_cost = st.number_input("Variable Cost per Unit ($)", value=5)
            price = st.number_input("Price per Unit ($)", value=15)
        
        with col2:
            # Profit calculations
            break_even = fixed_costs / (price - variable_cost)
            max_production = st.number_input("Maximum Production", value=500)
            
            st.metric("Break-even Point", f"{break_even:.0f} units")
            st.metric("Profit Margin", f"{(price - variable_cost)/price*100:.1f}%")
        
        # Profit function graph
        units = np.linspace(0, max_production, 100)
        revenue = price * units
        cost = fixed_costs + variable_cost * units
        profit = revenue - cost
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=units, y=revenue, mode='lines', name='Revenue', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=units, y=cost, mode='lines', name='Cost', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=units, y=profit, mode='lines', name='Profit', line=dict(color='blue')))
        
        fig.update_layout(
            title="Business Profit Analysis",
            xaxis_title="Units Produced",
            yaxis_title="Amount ($)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def render_geometry_problems(self):
        """Geometry problem solver"""
        st.subheader("📐 Geometry Problem Solver")
        
        problem_type = st.selectbox(
            "Select Geometry Problem:",
            ["Area of Shapes", "Pythagorean Theorem", "Volume Calculations"]
        )
        
        if problem_type == "Area of Shapes":
            shape = st.selectbox("Select Shape:", ["Rectangle", "Triangle", "Circle"])
            
            if shape == "Rectangle":
                length = st.number_input("Length", value=10.0)
                width = st.number_input("Width", value=5.0)
                area = length * width
                st.success(f"Area = {length} × {width} = {area}")
            
            elif shape == "Triangle":
                base = st.number_input("Base", value=10.0)
                height = st.number_input("Height", value=6.0)
                area = 0.5 * base * height
                st.success(f"Area = ½ × {base} × {height} = {area}")
            
            elif shape == "Circle":
                radius = st.number_input("Radius", value=5.0)
                area = np.pi * radius ** 2
                st.success(f"Area = π × {radius}² = {area:.2f}")
    
    def render_physics_applications(self):
        """Additional physics applications"""
        st.subheader("⚛️ Physics Applications")
        
        application = st.selectbox(
            "Select Physics Application:",
            ["Simple Harmonic Motion", "Ohm's Law", "Kinetic Energy", "Gravitational Force"]
        )
        
        if application == "Simple Harmonic Motion":
            st.latex(r"x(t) = A \cos(\omega t + \phi)")
            st.write("Where:")
            st.write("- A = amplitude")
            st.write("- ω = angular frequency") 
            st.write("- φ = phase angle")
            
        elif application == "Ohm's Law":
            st.latex(r"V = IR")
            st.write("Where:")
            st.write("- V = voltage (volts)")
            st.write("- I = current (amperes)")
            st.write("- R = resistance (ohms)")
            
        elif application == "Kinetic Energy":
            st.latex(r"KE = \frac{1}{2}mv^2")
            st.write("Where:")
            st.write("- m = mass (kg)")
            st.write("- v = velocity (m/s)")
            
        elif application == "Gravitational Force":
            st.latex(r"F = G\frac{m_1 m_2}{r^2}")
            st.write("Where:")
            st.write("- G = gravitational constant")
            st.write("- m₁, m₂ = masses")
            st.write("- r = distance between masses")
    
    def render_authentication(self):
        """Render authentication page"""
        st.markdown('<div class="section-header">🔐 Authentication</div>', unsafe_allow_html=True)
        if AUTH_AVAILABLE:
            render_login_register_forms()
        else:
            st.info("Authentication system is currently unavailable. Using guest mode.")
            if st.button("Continue as Guest"):
                st.session_state.is_authenticated = True
                st.session_state.show_auth = False
                st.rerun()
    
    def run(self):
        """Main application runner"""
        # Apply theme
        if THEME_AVAILABLE:
            st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
        else:
            # Basic CSS fallback
            st.markdown("""
            <style>
            .main-header { color: #1f77b4; text-align: center; }
            .section-header { color: #2e86ab; margin: 20px 0; font-size: 24px; }
            </style>
            """, unsafe_allow_html=True)
        
        # Header
        st.markdown(f'<h1 class="main-header">🧮 {config.APP_NAME}</h1>', unsafe_allow_html=True)
        st.markdown("### Interactive platform for learning and visualizing algebra concepts")
        
        # Check authentication
        if AUTH_AVAILABLE:
            initialize_auth()
        
        # Show authentication page if not authenticated
        if not st.session_state.is_authenticated and st.session_state.get('show_auth', False):
            self.render_authentication()
            return
        elif not st.session_state.is_authenticated:
            # Auto-continue as guest
            st.session_state.is_authenticated = True
        
        # Render sidebar
        self.render_sidebar()
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Dashboard", 
            "🎯 Quadratic Solver", 
            "📈 Polynomial Analyzer", 
            "🔬 Identity Prover",
            "🌍 Real World"
        ])
        
        with tab1:
            self.render_main_dashboard()
        
        with tab2:
            self.render_quadratic_solver()
        
        with tab3:
            self.render_polynomial_analyzer()
        
        with tab4:
            self.render_identity_prover()
        
        with tab5:
            self.render_real_world_apps()
        
        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🎨 Features**")
            st.write("• Multiple Themes")
            st.write("• Real-time Solving")
            st.write("• Step-by-Step Solutions")
        
        with col2:
            st.write("**📊 Analysis**")
            st.write("• Graphical Visualization")
            st.write("• Numerical Verification")
            st.write("• Geometric Proofs")
        
        with col3:
            st.write("**🚀 Advanced**")
            st.write("• Problem Generator")
            st.write("• Progress Tracking")
            st.write("• Real-world Applications")

# Run the application
if __name__ == "__main__":
    app = AlgebraVisualizerApp()
    app.run()

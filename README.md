# Advanced Algebra Visualizer 🧮

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-square&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-square)](LICENSE)

> **An Interactive Algebra Learning Platform with Real-time Visualization, Voice Commands, and Gamified Learning**

## 🌟 Overview

The **Advanced Algebra Visualizer** is a comprehensive web application that transforms abstract algebraic concepts into interactive, visual learning experiences. Built with Streamlit and powered by SymPy, it provides students and educators with powerful tools for exploring mathematics through dynamic visualization, step-by-step solutions, and engaging gamification.

![Algebra Visualizer Demo](https://via.placeholder.com/800x400.png?text=Advanced+Algebra+Visualizer+Interface)

## 🚀 Key Features

### 🔍 **Interactive Equation Solvers**
- **Quadratic Equation Solver**: Real-time solving with graphical representation
- **Polynomial Analyzer**: Root finding and factorization up to 6th degree
- **Step-by-Step Solutions**: Detailed algebraic procedures
- **Multiple Representations**: Symbolic, numeric, and graphical views

### 📊 **Advanced Visualization**
- **Real-time Graphing**: Interactive Plotly charts with zoom and pan
- **Root Visualization**: Complex plane representation for polynomials
- **Dynamic Updates**: Instant graphical feedback on parameter changes
- **Multiple Coordinate Systems**: Cartesian, polar, and 3D plotting

### 🎮 **Gamified Learning**
- **Progress Tracking**: User achievement system and level progression
- **Skill Mastery**: Concept-based proficiency tracking
- **Achievement Badges**: Motivational reward system
- **Learning Analytics**: Performance insights and recommendations

### 🎤 **Voice Command Interface**
- **Hands-free Operation**: Voice-controlled equation solving
- **Natural Language Processing**: Intuitive voice commands
- **Audio Feedback**: Spoken solutions and explanations
- **Accessibility Focus**: Enhanced usability for diverse learners

### 🔐 **User Management**
- **Secure Authentication**: Encrypted user registration and login
- **Personalized Profiles**: Custom learning paths and preferences
- **Progress Persistence**: Cloud-synced learning history
- **Multi-user Support**: Separate profiles for different users

### 🎨 **Customizable Experience**
- **Theme System**: Light/dark mode and custom color schemes
- **Responsive Design**: Mobile-friendly interface
- **Accessibility Options**: High contrast and font size controls
- **Export Capabilities**: Save graphs and solutions

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | Interactive web interface |
| **Mathematics** | SymPy, NumPy | Symbolic computation & numerical analysis |
| **Visualization** | Plotly, Matplotlib | Dynamic graphing & charts |
| **Database** | SQLite | User data & progress storage |
| **Voice Processing** | SpeechRecognition, pyttsx3 | Audio input/output |
| **Authentication** | Custom encryption | Secure user management |
| **Deployment** | Streamlit Sharing | Cloud hosting |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Web browser with HTML5 support

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/jeetukumarmeena/Advanced-Algerbra-Visualization-Pro.git
   cd Advanced-Algebra-Visualizer
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv algebra_env
   # On Windows:
   algebra_env\Scripts\activate
   # On macOS/Linux:
   source algebra_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python -c "from auth import init_db; init_db()"
   ```

5. **Launch the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

### Detailed Installation

<details>
<summary>Click to expand detailed installation instructions</summary>

#### Option A: Using requirements.txt
```bash
# Install all dependencies at once
pip install streamlit plotly numpy pandas sympy speechrecognition pyttsx3
```

#### Option B: Manual package installation
```bash
# Core framework
pip install streamlit==1.28.0

# Mathematics and data
pip install numpy==1.24.0 pandas==2.0.0 sympy==1.12

# Visualization
pip install plotly==5.15.0 matplotlib==3.7.0

# Voice processing
pip install SpeechRecognition==3.10.0 pyttsx3==2.90

# Additional utilities
pip install pillow==9.5.0 scipy==1.10.0
```

#### Database Setup
The application automatically creates the SQLite database in the `data/` directory. For manual setup:

```bash
mkdir data
python -c "from auth import init_db; init_db()"
```

</details>

## 🎯 Usage Guide

### Quadratic Equation Solver
1. Navigate to the "🎯 Quadratic Solver" tab
2. Select equation format: Standard, Vertex, or Factored
3. Adjust coefficients using sliders or direct input
4. View real-time solutions with step-by-step explanations
5. Analyze the graph for intercepts and vertex

### Polynomial Analyzer
1. Go to "📈 Polynomial Analyzer" tab
2. Select polynomial degree (1-6)
3. Enter coefficients for each term
4. View roots, factorization, and graphical representation
5. Explore complex roots on the complex plane

### Voice Commands
1. Click the microphone icon in any solver
2. Speak commands like:
   - "Solve two x squared plus three x minus five"
   - "Graph y equals x cubed minus two x"
   - "Factor x squared minus four"
3. Listen to spoken solutions and explanations

### Progress Tracking
1. Create a user account or login
2. Solve problems to earn points and level up
3. Unlock achievements and badges
4. Track your learning journey in the dashboard

## 📁 Project Structure

```
Advanced_Algebra/
├── app.py                          # Main application controller
├── math_engine.py                  # Core mathematical computations
├── visualizations.py               # Graphing and chart generation
├── gamification.py                 # Progress tracking & achievements
├── auth.py                         # User authentication system
├── voice_commands.py               # Speech recognition & processing
├── theme.py                        # UI theming and customization
├── config.py                       # Application configuration
├── documentation_generator.py      # Auto-documentation creation
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
└── data/
    ├── user_progress.db            # SQLite database
    └── assets/                     # Images and static files
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for custom configuration:

```env
# Application settings
DEBUG_MODE=False
DATABASE_PATH=./data/user_progress.db
MAX_FILE_SIZE=50MB

# Voice processing
VOICE_TIMEOUT=10
VOICE_ENERGY_THRESHOLD=300

# Theme settings
DEFAULT_THEME=light
ACCENT_COLOR=#FF4B4B
```

### Custom Themes
Modify `theme.py` to create custom color schemes:

```python
CUSTOM_THEME = {
    "primaryColor": "#FF4B4B",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#262730",
    "font": "sans serif"
}
```

## 🚀 Deployment

### Local Deployment
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Cloud Deployment (Streamlit Sharing)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Sharing"
   git push origin main
   ```

2. **Deploy on Streamlit Sharing**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file to `app.py`
   - Click "Deploy"

3. **Access your live application** at `https://your-app-name.streamlit.app`

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📊 Mathematical Capabilities

### Supported Equation Types
- **Linear Equations**: First-degree polynomial solving
- **Quadratic Equations**: Complete solution with discriminant analysis
- **Polynomial Equations**: Up to 6th degree with complex roots
- **Systems of Equations**: Linear system solving
- **Algebraic Identities**: Verification and proof

### Graphical Features
- **Real-time Plotting**: Instant graph updates
- **Multiple Functions**: Overlay multiple equations
- **Interactive Controls**: Zoom, pan, and data point inspection
- **Export Options**: Save graphs as PNG or PDF
- **Animation**: Dynamic parameter changes

## 👥 User Management

### User Roles
- **Student**: Full access to learning features
- **Educator**: Additional classroom management tools
- **Administrator**: System configuration and user management

### Progress Tracking
- **Concept Mastery**: Track proficiency across algebraic topics
- **Problem History**: Review past solutions and approaches
- **Learning Analytics**: Identify strengths and areas for improvement
- **Achievement System**: Motivational goals and rewards

## 🎤 Voice Command Reference

### Basic Commands
```
"Solve [equation]"           # Solve algebraic equations
"Graph [function]"           # Plot mathematical functions
"Factor [expression]"        # Factor algebraic expressions
"Simplify [expression]"      # Simplify mathematical expressions
"Derivative of [function]"   # Calculate derivatives
```

### Example Phrases
```
"Solve two x squared plus five x minus three equals zero"
"Graph y equals sine x from zero to two pi"
"Factor x squared minus four"
"Simplify x squared plus two x plus one divided by x plus one"
```

## 🔒 Security Features

- **Password Hashing**: bcrypt-based encryption
- **Session Management**: Secure user sessions
- **Input Validation**: Protection against injection attacks
- **Data Privacy**: Local storage option for sensitive data
- **Secure APIs**: Validated mathematical input processing

## 🐛 Troubleshooting

### Common Issues

**Issue**: Module not found errors
```bash
# Solution: Reinstall requirements
pip install -r requirements.txt
```

**Issue**: Voice commands not working
```bash
# Solution: Install additional dependencies
pip install pyaudio
# On Windows, you might need:
pip install pipwin
pipwin install pyaudio
```

**Issue**: Database connection errors
```bash
# Solution: Reinitialize database
python -c "from auth import init_db; init_db()"
```

**Issue**: Port already in use
```bash
# Solution: Use different port
streamlit run app.py --server.port 8502
```

### Getting Help

1. Check the application logs in the terminal
2. Verify all dependencies are installed correctly
3. Ensure microphone permissions are granted (for voice features)
4. Check the browser console for JavaScript errors

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use descriptive variable names
- Add docstrings to all functions
- Include type hints where possible

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** team for the amazing web framework
- **SymPy** community for robust symbolic mathematics
- **Plotly** for interactive visualization capabilities
- **Python** community for comprehensive libraries
- **Educators and students** for valuable feedback and testing

## 📞 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/jeetukumarmeena/Advanced-Algerbra-Visualization-Pro/issues)
- **Email**: [Your Email]
- **Discussions**: [GitHub Discussions](https://github.com/jeetukumarmeena/Advanced-Algerbra-Visualization-Pro/discussions)

## 🚀 Future Roadmap

- [ ] **Mobile App** - iOS and Android versions
- [ ] **AI Tutor** - Personalized learning recommendations
- [ ] **3D Graphing** - Three-dimensional function visualization
- [ ] **Collaborative Features** - Multi-user problem solving
- [ ] **Curriculum Integration** - Standard-aligned lesson plans
- [ ] **Offline Mode** - Functionality without internet connection
- [ ] **Multi-language Support** - Internationalization
- [ ] **Advanced Calculus** - Integration and differentiation tools

---

<div align="center">

**Made with ❤️ for the Mathematics Education Community**

*Empowering students to see the beauty in algebra through interactive visualization*

[![Star History Chart](https://api.star-history.com/svg?repos=jeetukumarmeena/Advanced-Algerbra-Visualization-Pro&type=Date)](https://star-history.com/#jeetukumarmeena/Advanced-Algerbra-Visualization-Pro&Date)

</div>

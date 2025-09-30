import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit as st
from math_engine import math_engine

class Visualizations:
    def __init__(self):
        self.colors = ['#4FD1C7', '#F56565', '#48BB78', '#ED8936', '#9F7AEA']
    
    def create_quadratic_plot(self, a, b, c, x_range=(-10, 10)):
        """Create quadratic function plot with analysis"""
        x = np.linspace(x_range[0], x_range[1], 400)
        y = a*x**2 + b*x + c
        
        fig = go.Figure()
        
        # Main curve
        fig.add_trace(go.Scatter(
            x=x, y=y, 
            mode='lines', 
            name=f'{a}x² + {b}x + {c}',
            line=dict(width=4, color=self.colors[0])
        ))
        
        # Analysis
        solution = math_engine.solve_quadratic(a, b, c)
        vertex_x = -b/(2*a)
        vertex_y = a*vertex_x**2 + b*vertex_x + c
        
        # Add vertex
        fig.add_trace(go.Scatter(
            x=[vertex_x], y=[vertex_y],
            mode='markers',
            marker=dict(size=12, color=self.colors[1]),
            name='Vertex'
        ))
        
        # Add roots if real
        if solution["type"] in ["real", "double"]:
            roots = solution["roots"]
            fig.add_trace(go.Scatter(
                x=roots, y=np.zeros(len(roots)),
                mode='markers',
                marker=dict(size=10, color=self.colors[2]),
                name='Roots'
            ))
        
        fig.update_layout(
            title=f"Quadratic Function Analysis",
            xaxis_title="x",
            yaxis_title="f(x)",
            showlegend=True,
            height=500,
            template="plotly_dark"
        )
        
        return fig
    
    def create_3d_surface(self, expression, x_range=(-5,5), y_range=(-5,5)):
        """Create 3D surface plot"""
        x = np.linspace(x_range[0], x_range[1], 50)
        y = np.linspace(y_range[0], y_range[1], 50)
        X, Y = np.meshgrid(x, y)
        
        # Safe evaluation of expression
        try:
            Z = eval(expression, {"np": np, "X": X, "Y": Y, "x": X, "y": Y})
        except:
            Z = X + Y  # Fallback
        
        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
        
        fig.update_layout(
            title=f'3D Surface: z = {expression}',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=600
        )
        
        return fig
    
    def create_geometric_proof(self, a, b, identity_type):
        """Create geometric proof visualization"""
        if identity_type == "(a + b)²":
            return self._create_square_proof(a, b)
        elif identity_type == "a² - b²":
            return self._create_difference_of_squares(a, b)
        
        return None
    
    def _create_square_proof(self, a, b):
        """Geometric proof of (a+b)²"""
        fig = go.Figure()
        
        # Large square
        fig.add_trace(go.Scatter(
            x=[0, a+b, a+b, 0, 0],
            y=[0, 0, a+b, a+b, 0],
            fill="toself",
            fillcolor="rgba(79, 209, 199, 0.2)",
            line=dict(color="#4FD1C7", width=3),
            name=f'Area = (a+b)² = {(a+b)**2}'
        ))
        
        # Add grid lines
        fig.add_shape(type="line", x0=a, y0=0, x1=a, y1=a+b,
                     line=dict(color="white", width=2, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=a, x1=a+b, y1=a,
                     line=dict(color="white", width=2, dash="dash"))
        
        # Add labels
        annotations = [
            dict(x=a/2, y=-0.3, text=f"a = {a}", showarrow=False, font=dict(color="white")),
            dict(x=a + b/2, y=-0.3, text=f"b = {b}", showarrow=False, font=dict(color="white")),
            dict(x=-0.3, y=a/2, text=f"a = {a}", showarrow=False, font=dict(color="white")),
            dict(x=-0.3, y=a + b/2, text=f"b = {b}", showarrow=False, font=dict(color="white"))
        ]
        
        fig.update_layout(
            title="Geometric Proof of (a+b)² = a² + 2ab + b²",
            xaxis_range=[-1, a+b+1],
            yaxis_range=[-1, a+b+1],
            showlegend=True,
            annotations=annotations,
            height=500,
            template="plotly_dark"
        )
        
        return fig
    
    def create_convergence_plot(self, values, target, title):
        """Plot convergence of iterative methods"""
        iterations = list(range(1, len(values) + 1))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=iterations, y=values,
            mode='lines+markers',
            name='Approximation',
            line=dict(width=3, color=self.colors[0])
        ))
        
        fig.add_hline(y=target, line_dash="dash", 
                     line_color="red", 
                     annotation_text=f"Target: {target}")
        
        fig.update_layout(
            title=title,
            xaxis_title="Iterations",
            yaxis_title="Value",
            height=400,
            template="plotly_dark"
        )
        
        return fig

# Global instance
viz = Visualizations()
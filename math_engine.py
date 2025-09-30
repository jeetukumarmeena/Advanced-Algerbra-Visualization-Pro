import numpy as np
import sympy as sp
from sympy import symbols, expand, factor, solve, simplify, diff, integrate, latex
import plotly.graph_objects as go
import plotly.express as px
from functools import lru_cache
import streamlit as st

class MathEngine:
    def __init__(self):
        self.x, self.y, self.z, self.a, self.b, self.c = symbols('x y z a b c')
    
    @st.cache_data(ttl=3600)
    def solve_quadratic(_self, a, b, c):
        """Solve quadratic equation with caching"""
        discriminant = b**2 - 4*a*c
        
        if discriminant > 0:
            root1 = (-b + np.sqrt(discriminant)) / (2*a)
            root2 = (-b - np.sqrt(discriminant)) / (2*a)
            return {"type": "real", "roots": [root1, root2], "discriminant": discriminant}
        elif discriminant == 0:
            root = -b / (2*a)
            return {"type": "double", "roots": [root], "discriminant": discriminant}
        else:
            real_part = -b / (2*a)
            imag_part = np.sqrt(-discriminant) / (2*a)
            return {"type": "complex", "roots": [real_part, imag_part], "discriminant": discriminant}
    
    def expand_expression(self, expression):
        """Expand algebraic expression"""
        try:
            expr = sp.sympify(expression)
            expanded = expand(expr)
            return {
                "original": latex(expr),
                "expanded": latex(expanded),
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def factor_expression(self, expression):
        """Factor algebraic expression"""
        try:
            expr = sp.sympify(expression)
            factored = factor(expr)
            return {
                "original": latex(expr),
                "factored": latex(factored),
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def solve_polynomial(self, coefficients):
        """Solve polynomial equation"""
        try:
            roots = np.roots(coefficients)
            real_roots = [r for r in roots if abs(r.imag) < 1e-10]
            complex_roots = [r for r in roots if abs(r.imag) >= 1e-10]
            
            return {
                "all_roots": roots,
                "real_roots": real_roots,
                "complex_roots": complex_roots,
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_derivative(self, expression, variable='x'):
        """Calculate derivative of expression"""
        try:
            var = symbols(variable)
            expr = sp.sympify(expression)
            derivative = diff(expr, var)
            
            return {
                "function": latex(expr),
                "derivative": latex(derivative),
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_integral(self, expression, variable='x'):
        """Calculate integral of expression"""
        try:
            var = symbols(variable)
            expr = sp.sympify(expression)
            integral = integrate(expr, var)
            
            return {
                "function": latex(expr),
                "integral": latex(integral),
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def prove_identity(self, left_side, right_side):
        """Prove algebraic identity"""
        try:
            left_expr = sp.sympify(left_side)
            right_expr = sp.sympify(right_side)
            
            # Check if they are equal by simplifying difference
            difference = simplify(left_expr - right_expr)
            
            return {
                "left_side": latex(left_expr),
                "right_side": latex(right_expr),
                "is_identity": difference == 0,
                "difference": latex(difference),
                "success": True
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
math_engine = MathEngine()
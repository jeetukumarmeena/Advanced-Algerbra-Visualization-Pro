"""
Calculation functions for Algebra Visualizer Pro
"""

import math
from typing import Union, Tuple, List, Optional

def calculate_discriminant(a: float, b: float, c: float) -> float:
    """
    Calculate discriminant of quadratic equation
    
    Args:
        a: Coefficient a
        b: Coefficient b  
        c: Coefficient c
        
    Returns:
        Discriminant value
    """
    return b**2 - 4*a*c

def calculate_vertex(a: float, b: float, c: float) -> Tuple[float, float]:
    """
    Calculate vertex of quadratic function
    
    Args:
        a: Coefficient a
        b: Coefficient b
        c: Coefficient c
        
    Returns:
        Tuple of (x, y) coordinates of vertex
    """
    x_vertex = -b / (2*a)
    y_vertex = a*x_vertex**2 + b*x_vertex + c
    return (x_vertex, y_vertex)

def calculate_roots(a: float, b: float, c: float) -> Tuple[Optional[float], Optional[float], str]:
    """
    Calculate roots of quadratic equation
    
    Args:
        a: Coefficient a
        b: Coefficient b
        c: Coefficient c
        
    Returns:
        Tuple of (root1, root2, root_type)
    """
    discriminant = calculate_discriminant(a, b, c)
    
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return (root1, root2, "real_distinct")
    elif discriminant == 0:
        root = -b / (2*a)
        return (root, root, "real_equal")
    else:
        real_part = -b / (2*a)
        imag_part = math.sqrt(-discriminant) / (2*a)
        return (real_part, imag_part, "complex")

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate distance between two points
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Distance between points
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_slope(x1: float, y1: float, x2: float, y2: float) -> Optional[float]:
    """
    Calculate slope between two points
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Slope value or None if vertical line
    """
    if x2 - x1 == 0:
        return None  # Vertical line
    return (y2 - y1) / (x2 - x1)

def calculate_midpoint(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float]:
    """
    Calculate midpoint between two points
    
    Args:
        x1, y1: Coordinates of first point
        x2, y2: Coordinates of second point
        
    Returns:
        Tuple of (x, y) coordinates of midpoint
    """
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def calculate_quadratic_value(a: float, b: float, c: float, x: float) -> float:
    """
    Calculate value of quadratic function at given x
    
    Args:
        a, b, c: Quadratic coefficients
        x: x-coordinate
        
    Returns:
        Function value at x
    """
    return a*x**2 + b*x + c

def calculate_derivative_at_point(coefficients: List[float], x: float) -> float:
    """
    Calculate derivative of polynomial at given point
    
    Args:
        coefficients: List of coefficients [a, b, c, ...] for ax² + bx + c
        x: Point to evaluate derivative at
        
    Returns:
        Derivative value at x
    """
    derivative = 0
    for i, coeff in enumerate(coefficients):
        if i > 0:  # Skip constant term for derivative
            derivative += i * coeff * (x ** (i - 1))
    return derivative

def calculate_area_under_curve(a: float, b: float, c: float, 
                             x_start: float, x_end: float) -> float:
    """
    Calculate approximate area under quadratic curve using trapezoidal rule
    
    Args:
        a, b, c: Quadratic coefficients
        x_start: Start of interval
        x_end: End of interval
        
    Returns:
        Approximate area under curve
    """
    # Use trapezoidal rule with 100 segments
    n_segments = 100
    dx = (x_end - x_start) / n_segments
    area = 0
    
    for i in range(n_segments):
        x1 = x_start + i * dx
        x2 = x1 + dx
        y1 = calculate_quadratic_value(a, b, c, x1)
        y2 = calculate_quadratic_value(a, b, c, x2)
        area += (y1 + y2) * dx / 2
    
    return area

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def calculate_average(values: List[float]) -> float:
    """
    Calculate average of values
    
    Args:
        values: List of numerical values
        
    Returns:
        Average value
    """
    if not values:
        return 0
    return sum(values) / len(values)

def calculate_standard_deviation(values: List[float]) -> float:
    """
    Calculate standard deviation of values
    
    Args:
        values: List of numerical values
        
    Returns:
        Standard deviation
    """
    if len(values) < 2:
        return 0
    
    mean = calculate_average(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)
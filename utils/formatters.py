"""
Formatting functions for Algebra Visualizer Pro
"""

import math
from typing import Union, List
from datetime import datetime

def format_latex(expression: str) -> str:
    """
    Format expression for LaTeX display
    
    Args:
        expression: Math expression
        
    Returns:
        LaTeX formatted string
    """
    if not expression:
        return ""
    
    # Basic LaTeX formatting
    latex_replacements = {
        '^': '^',
        'sqrt': '\\sqrt',
        'pi': '\\pi',
        'infty': '\\infty',
        'alpha': '\\alpha',
        'beta': '\\beta',
        'gamma': '\\gamma',
        'theta': '\\theta'
    }
    
    formatted = expression
    for old, new in latex_replacements.items():
        formatted = formatted.replace(old, new)
    
    return f"${formatted}$"

def format_number(number: Union[int, float], precision: int = 2) -> str:
    """
    Format number with appropriate precision
    
    Args:
        number: Number to format
        precision: Decimal precision
        
    Returns:
        Formatted number string
    """
    if number is None:
        return "N/A"
    
    if isinstance(number, int):
        return str(number)
    
    if math.isnan(number) or math.isinf(number):
        return str(number)
    
    # Format with specified precision
    return f"{number:.{precision}f}"

def format_percentage(value: float, precision: int = 1) -> str:
    """
    Format percentage value
    
    Args:
        value: Percentage value (0-100)
        precision: Decimal precision
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{precision}f}%"

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds} seconds"
    
    minutes = seconds // 60
    if minutes < 60:
        remaining_seconds = seconds % 60
        return f"{minutes} minutes {remaining_seconds} seconds"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if hours < 24:
        return f"{hours} hours {remaining_minutes} minutes"
    
    days = hours // 24
    remaining_hours = hours % 24
    return f"{days} days {remaining_hours} hours"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable string
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

def format_list_as_string(items: List[str], conjunction: str = "and") -> str:
    """
    Format list as natural language string
    
    Args:
        items: List of items
        conjunction: Conjunction to use
        
    Returns:
        Formatted string
    """
    if not items:
        return ""
    
    if len(items) == 1:
        return items[0]
    
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    
    return ", ".join(items[:-1]) + f", {conjunction} {items[-1]}"

def format_timestamp(timestamp: datetime, format_str: str = None) -> str:
    """
    Format timestamp
    
    Args:
        timestamp: Datetime object
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if format_str is None:
        format_str = "%Y-%m-%d %H:%M:%S"
    
    return timestamp.strftime(format_str)

def format_math_fraction(numerator: float, denominator: float) -> str:
    """
    Format fraction for mathematical display
    
    Args:
        numerator: Numerator
        denominator: Denominator
        
    Returns:
        Formatted fraction string
    """
    if denominator == 1:
        return str(numerator)
    
    return f"{numerator}/{denominator}"

def format_complex_number(real: float, imag: float) -> str:
    """
    Format complex number
    
    Args:
        real: Real part
        imag: Imaginary part
        
    Returns:
        Formatted complex number string
    """
    if imag == 0:
        return str(real)
    
    if real == 0:
        return f"{imag}i"
    
    sign = "+" if imag >= 0 else ""
    return f"{real} {sign} {abs(imag)}i"
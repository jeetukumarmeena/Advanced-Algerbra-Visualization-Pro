"""
Validation functions for Algebra Visualizer Pro
"""

import re
import math
from typing import Union, Tuple, List
from .constants import ERROR_MESSAGES

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email address is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, ""
    else:
        return False, "Please enter a valid email address"

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit"
    
    return True, ""

def validate_math_expression(expression: str, allowed_vars: List[str] = None) -> Tuple[bool, str]:
    """
    Validate mathematical expression
    
    Args:
        expression: Math expression to validate
        allowed_vars: List of allowed variable names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not expression:
        return False, "Expression cannot be empty"
    
    if allowed_vars is None:
        allowed_vars = ['x', 'y', 'z', 'a', 'b', 'c']
    
    # Check for dangerous operations
    dangerous_patterns = [
        r'__',  # Double underscore (could be used for magic methods)
        r'import',
        r'eval',
        r'exec',
        r'open',
        r'file',
        r'os\.',
        r'sys\.'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, expression, re.IGNORECASE):
            return False, "Expression contains unsafe operations"
    
    # Check for valid variable names
    var_pattern = r'[a-zA-Z_][a-zA-Z0-9_]*'
    variables = re.findall(var_pattern, expression)
    
    for var in variables:
        if var not in allowed_vars and var not in ['sqrt', 'sin', 'cos', 'tan', 'log', 'exp', 'pi', 'e']:
            return False, f"Invalid variable or function: {var}"
    
    return True, ""

def validate_coefficients(a: float, b: float = None, c: float = None) -> Tuple[bool, str]:
    """
    Validate equation coefficients
    
    Args:
        a: Coefficient a
        b: Coefficient b (optional)
        c: Coefficient c (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if a == 0:
        return False, "Coefficient 'a' cannot be zero for quadratic equations"
    
    if not isinstance(a, (int, float)):
        return False, "Coefficient 'a' must be a number"
    
    if b is not None and not isinstance(b, (int, float)):
        return False, "Coefficient 'b' must be a number"
    
    if c is not None and not isinstance(c, (int, float)):
        return False, "Coefficient 'c' must be a number"
    
    return True, ""

def validate_range(value: float, min_val: float, max_val: float, value_name: str = "Value") -> Tuple[bool, str]:
    """
    Validate value is within specified range
    
    Args:
        value: Value to check
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        value_name: Name of the value for error message
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, (int, float)):
        return False, f"{value_name} must be a number"
    
    if value < min_val:
        return False, f"{value_name} must be at least {min_val}"
    
    if value > max_val:
        return False, f"{value_name} must be at most {max_val}"
    
    return True, ""

def validate_file_upload(file, allowed_types: List[str] = None, max_size: int = None) -> Tuple[bool, str]:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file object
        allowed_types: List of allowed MIME types
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if allowed_types is None:
        allowed_types = ['text/csv', 'application/json', 'image/png', 'image/jpeg']
    
    if max_size is None:
        max_size = 10 * 1024 * 1024  # 10MB
    
    if file.size > max_size:
        return False, f"File size must be less than {max_size // (1024*1024)}MB"
    
    if file.type not in allowed_types:
        return False, f"File type {file.type} is not supported"
    
    return True, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 20:
        return False, "Username must be at most 20 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""
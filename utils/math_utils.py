"""
Mathematical utility functions for Algebra Visualizer Pro
"""

import math
from typing import Union, List, Tuple
import sympy as sp

def solve_linear_equation(a: float, b: float, c: float) -> float:
    """
    Solve linear equation ax + b = c
    
    Args:
        a: Coefficient a
        b: Coefficient b
        c: Constant c
        
    Returns:
        Solution for x
    """
    if a == 0:
        raise ValueError("Coefficient 'a' cannot be zero")
    return (c - b) / a

def factor_expression(expression: str) -> str:
    """
    Factor algebraic expression using sympy
    
    Args:
        expression: Algebraic expression to factor
        
    Returns:
        Factored expression
    """
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(expression)
        factored = sp.factor(expr)
        return str(factored)
    except:
        return expression  # Return original if factoring fails

def expand_expression(expression: str) -> str:
    """
    Expand algebraic expression using sympy
    
    Args:
        expression: Algebraic expression to expand
        
    Returns:
        Expanded expression
    """
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(expression)
        expanded = sp.expand(expr)
        return str(expanded)
    except:
        return expression

def simplify_expression(expression: str) -> str:
    """
    Simplify algebraic expression using sympy
    
    Args:
        expression: Algebraic expression to simplify
        
    Returns:
        Simplified expression
    """
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(expression)
        simplified = sp.simplify(expr)
        return str(simplified)
    except:
        return expression

def find_common_factors(numbers: List[int]) -> List[int]:
    """
    Find common factors of a list of numbers
    
    Args:
        numbers: List of integers
        
    Returns:
        List of common factors
    """
    if not numbers:
        return []
    
    min_number = min(numbers)
    factors = []
    
    for i in range(1, min_number + 1):
        if all(num % i == 0 for num in numbers):
            factors.append(i)
    
    return factors

def calculate_gcd(a: int, b: int) -> int:
    """
    Calculate greatest common divisor using Euclidean algorithm
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        GCD of a and b
    """
    while b != 0:
        a, b = b, a % b
    return abs(a)

def calculate_lcm(a: int, b: int) -> int:
    """
    Calculate least common multiple
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        LCM of a and b
    """
    return abs(a * b) // calculate_gcd(a, b) if a and b else 0

def is_prime(n: int) -> bool:
    """
    Check if number is prime
    
    Args:
        n: Number to check
        
    Returns:
        True if number is prime
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True

def prime_factors(n: int) -> List[int]:
    """
    Find prime factors of a number
    
    Args:
        n: Number to factor
        
    Returns:
        List of prime factors
    """
    factors = []
    divisor = 2
    
    while n > 1:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 1
    
    return factors

def factorial(n: int) -> int:
    """
    Calculate factorial of a number
    
    Args:
        n: Number
        
    Returns:
        Factorial value
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def combinations(n: int, k: int) -> int:
    """
    Calculate combinations (n choose k)
    
    Args:
        n: Total items
        k: Items to choose
        
    Returns:
        Number of combinations
    """
    if k < 0 or k > n:
        return 0
    return factorial(n) // (factorial(k) * factorial(n - k))

def permutations(n: int, k: int) -> int:
    """
    Calculate permutations
    
    Args:
        n: Total items
        k: Items to arrange
        
    Returns:
        Number of permutations
    """
    if k < 0 or k > n:
        return 0
    return factorial(n) // factorial(n - k)

def solve_system_2x2(a1: float, b1: float, c1: float, 
                    a2: float, b2: float, c2: float) -> Tuple[float, float]:
    """
    Solve 2x2 system of linear equations
    
    Args:
        a1, b1, c1: Coefficients for first equation
        a2, b2, c2: Coefficients for second equation
        
    Returns:
        Tuple (x, y) solution
    """
    determinant = a1 * b2 - a2 * b1
    
    if determinant == 0:
        raise ValueError("System has no unique solution")
    
    x = (c1 * b2 - c2 * b1) / determinant
    y = (a1 * c2 - a2 * c1) / determinant
    
    return (x, y)
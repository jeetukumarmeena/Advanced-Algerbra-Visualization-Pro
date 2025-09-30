"""
Data generation functions for Algebra Visualizer Pro
"""

import random
import math
from typing import List, Dict, Any, Tuple
from .constants import DIFFICULTY_LEVELS, PROBLEM_TYPES

def generate_quadratic_problem(difficulty: str = "medium") -> Dict[str, Any]:
    """
    Generate a quadratic equation problem
    
    Args:
        difficulty: Problem difficulty level
        
    Returns:
        Dictionary with problem data
    """
    diff_config = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])
    max_coeff = diff_config["max_coefficient"]
    
    # Generate coefficients that will yield real roots
    a = random.randint(1, max_coeff // 2)
    
    # Ensure discriminant is positive
    while True:
        b = random.randint(-max_coeff, max_coeff)
        c = random.randint(-max_coeff, max_coeff)
        discriminant = b**2 - 4*a*c
        if discriminant >= 0:
            break
    
    problem_text = f"Solve: {a}x² + {b}x + {c} = 0"
    
    # Calculate roots
    root1 = (-b + math.sqrt(discriminant)) / (2*a)
    root2 = (-b - math.sqrt(discriminant)) / (2*a)
    
    solution = f"x = {root1:.2f}, x = {root2:.2f}"
    
    return {
        "text": problem_text,
        "type": "quadratic",
        "difficulty": difficulty,
        "coefficients": {"a": a, "b": b, "c": c},
        "solution": solution,
        "discriminant": discriminant,
        "roots": [root1, root2]
    }

def generate_linear_problem(difficulty: str = "medium") -> Dict[str, Any]:
    """
    Generate a linear equation problem
    
    Args:
        difficulty: Problem difficulty level
        
    Returns:
        Dictionary with problem data
    """
    diff_config = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])
    max_coeff = diff_config["max_coefficient"]
    
    a = random.randint(1, max_coeff)
    b = random.randint(1, max_coeff)
    c = random.randint(b + 1, b + max_coeff)
    
    problem_text = f"Solve: {a}x + {b} = {c}"
    solution = f"x = {(c - b) / a:.2f}"
    
    return {
        "text": problem_text,
        "type": "linear",
        "difficulty": difficulty,
        "coefficients": {"a": a, "b": b, "c": c},
        "solution": solution
    }

def generate_factoring_problem(difficulty: str = "medium") -> Dict[str, Any]:
    """
    Generate a factoring problem
    
    Args:
        difficulty: Problem difficulty level
        
    Returns:
        Dictionary with problem data
    """
    diff_config = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])
    max_coeff = diff_config["max_coefficient"]
    
    # Generate factors first, then multiply
    factor1 = random.randint(1, max_coeff // 2)
    factor2 = random.randint(1, max_coeff // 2)
    
    # Create quadratic expression: (ax + b)(cx + d)
    a = random.randint(1, 3)
    b = random.randint(1, 5)
    c = random.randint(1, 3)
    d = random.randint(1, 5)
    
    # Expand: acx² + (ad + bc)x + bd
    expanded_a = a * c
    expanded_b = a*d + b*c
    expanded_c = b * d
    
    problem_text = f"Factor: {expanded_a}x² + {expanded_b}x + {expanded_c}"
    solution = f"({a}x + {b})({c}x + {d})"
    
    return {
        "text": problem_text,
        "type": "factoring",
        "difficulty": difficulty,
        "coefficients": {"a": expanded_a, "b": expanded_b, "c": expanded_c},
        "solution": solution
    }

def generate_random_expression(difficulty: str = "medium", variables: List[str] = None) -> str:
    """
    Generate a random algebraic expression
    
    Args:
        difficulty: Expression difficulty
        variables: List of variables to use
        
    Returns:
        Random algebraic expression
    """
    if variables is None:
        variables = ['x', 'y']
    
    diff_config = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])
    max_coeff = diff_config["max_coefficient"]
    
    # Generate number of terms (2-4)
    num_terms = random.randint(2, 4)
    terms = []
    
    for _ in range(num_terms):
        coeff = random.randint(1, max_coeff)
        var = random.choice(variables)
        
        # Decide if it's a simple term or has exponent
        if random.random() > 0.7:  # 30% chance of exponent
            exponent = random.randint(2, 3)
            term = f"{coeff}{var}^{exponent}"
        else:
            term = f"{coeff}{var}"
        
        terms.append(term)
    
    # Add operators
    expression = terms[0]
    for i in range(1, len(terms)):
        operator = random.choice(["+", "-"])
        expression += f" {operator} {terms[i]}"
    
    return expression

def generate_quiz_question(topic: str, difficulty: str = "medium") -> Dict[str, Any]:
    """
    Generate a multiple choice quiz question
    
    Args:
        topic: Question topic
        difficulty: Question difficulty
        
    Returns:
        Dictionary with quiz question data
    """
    questions = {
        "quadratic": [
            {
                "question": "What is the quadratic formula?",
                "options": [
                    "x = (-b ± √(b² - 4ac)) / 2a",
                    "x = (-b ± √(b² + 4ac)) / 2a", 
                    "x = (b ± √(b² - 4ac)) / 2a",
                    "x = (-b ± √(b² - 4ac)) / a"
                ],
                "correct": 0
            }
        ],
        "factoring": [
            {
                "question": "What is the factored form of x² - 9?",
                "options": [
                    "(x - 3)(x + 3)",
                    "(x - 3)(x - 3)",
                    "(x + 3)(x + 3)", 
                    "(x - 9)(x + 1)"
                ],
                "correct": 0
            }
        ],
        "linear": [
            {
                "question": "What is the solution to 2x + 5 = 13?",
                "options": ["x = 4", "x = 5", "x = 6", "x = 7"],
                "correct": 0
            }
        ]
    }
    
    topic_questions = questions.get(topic, questions["quadratic"])
    question_data = random.choice(topic_questions)
    
    return {
        "question": question_data["question"],
        "options": question_data["options"],
        "correct_index": question_data["correct"],
        "topic": topic,
        "difficulty": difficulty
    }

def generate_practice_set(problem_types: List[str], num_problems: int = 5, 
                         difficulty: str = "medium") -> List[Dict[str, Any]]:
    """
    Generate a set of practice problems
    
    Args:
        problem_types: Types of problems to include
        num_problems: Number of problems to generate
        difficulty: Problem difficulty
        
    Returns:
        List of problem dictionaries
    """
    problems = []
    generators = {
        "quadratic": generate_quadratic_problem,
        "linear": generate_linear_problem,
        "factoring": generate_factoring_problem
    }
    
    for _ in range(num_problems):
        problem_type = random.choice(problem_types)
        generator = generators.get(problem_type, generate_linear_problem)
        problem = generator(difficulty)
        problems.append(problem)
    
    return problems
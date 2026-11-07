from langchain_core.tools import tool
"""Adult BMI screening calculation tool."""

@tool
def calculate_bmi(weight_kg: float, height_cm: float) -> str:
    """Calculate adult BMI using weight in kilograms and height in centimeters. Not a medical diagnosis."""
    if weight_kg <= 0 or height_cm <= 0:
        return "Error: weight and height must be positive."
    bmi = weight_kg / (height_cm / 100) ** 2
    category = ("Underweight" if bmi < 18.5 else "Healthy weight" if bmi < 25
                else "Overweight" if bmi < 30 else "Obesity")
    return f"BMI: {bmi:.1f}. Standard adult BMI category: {category}. BMI is a screening measure, not a diagnosis."

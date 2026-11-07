"""Expose all four tools to the AI agent."""
from .age_tool import calculate_age
from .bmi_tool import calculate_bmi
from .date_difference_tool import calculate_date_difference
from .calculator_tool import calculate_calculator

ALL_TOOLS = [
    calculate_age,
    calculate_bmi,
    calculate_date_difference,
    calculate_calculator,
]

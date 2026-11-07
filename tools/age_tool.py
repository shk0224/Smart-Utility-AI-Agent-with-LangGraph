from langchain_core.tools import tool
"""Age calculation tool."""
from datetime import date

@tool
def calculate_age(birth_date: str, as_of_date: str = "") -> str:
    """Calculate exact age in years, months and days. Dates use YYYY-MM-DD; as_of_date defaults to today."""
    born = date.fromisoformat(birth_date)
    today = date.fromisoformat(as_of_date) if as_of_date else date.today()
    if born > today:
        return "Error: birth date cannot be in the future."
    years = today.year - born.year
    months = today.month - born.month
    days = today.day - born.day
    if days < 0:
        from calendar import monthrange
        previous_month = today.month - 1 or 12
        previous_year = today.year if today.month > 1 else today.year - 1
        days += monthrange(previous_year, previous_month)[1]
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return f"Age as of {today}: {years} years, {months} months, {days} days."

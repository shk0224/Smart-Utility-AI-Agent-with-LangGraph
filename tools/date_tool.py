from langchain_core.tools import tool
"""Date difference calculation tool."""
from datetime import date

@tool
def calculate_date_difference(start_date: str, end_date: str) -> str:
    """Find elapsed days and weeks between two dates in YYYY-MM-DD format (exclusive of the start date)."""
    first = date.fromisoformat(start_date)
    second = date.fromisoformat(end_date)
    days = (second - first).days
    sign = "before" if days < 0 else "after" if days > 0 else "the same day as"
    return f"{end_date} is {abs(days)} day(s) ({abs(days)//7} weeks and {abs(days)%7} days) {sign} {start_date}."

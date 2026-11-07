from langchain_core.tools import tool
"""Safe arithmetic expression tool."""
import ast
import math
import operator

_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
    ast.UAdd: operator.pos, ast.USub: operator.neg,
}

def _safe_arithmetic(expression: str) -> float:
    """Evaluate arithmetic AST only; reject names, calls and other Python syntax."""
    if len(expression) > 200:
        raise ValueError("Expression is too long")
    parsed = ast.parse(expression, mode="eval")

    def visit(node, depth=0):
        if depth > 20:
            raise ValueError("Expression is too deeply nested")
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 1e12:
                raise ValueError("Number is too large")
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd, ast.USub):
            return _OPERATORS[type(node.op)](visit(node.operand, depth + 1))
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            left = visit(node.left, depth + 1)
            right = visit(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and (abs(right) > 12 or abs(left) > 1e6):
                raise ValueError("Exponent too large")
            result = _OPERATORS[type(node.op)](left, right)
            if not math.isfinite(result) or abs(result) > 1e15:
                raise ValueError("Result is too large")
            return result
        raise ValueError("Only numbers, parentheses, +, -, *, /, //, %, and ** are supported")

    return visit(parsed.body)

@tool
def calculate_calculator(expression: str) -> str:
    """Calculate arithmetic expressions: +, -, *, /, //, %, ** and parentheses. For percentage, use e.g. 15/100*200."""
    try:
        result = _safe_arithmetic(expression)
        return f"{expression} = {result:g}"
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError, TypeError) as error:
        return f"Calculation error: {error}"


"""Smart Utility AI - LangGraph workflow with exactly four tool nodes."""

import os
import json
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from tools import ALL_TOOLS
from tools.age_tool import calculate_age
from tools.bmi_tool import calculate_bmi
from tools.date_tool import calculate_date_difference
from tools.calculator_tool import calculate_calculator


load_dotenv()


# =========================
# LLM
# =========================

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    temperature=0
)

llm_with_tools = llm.bind_tools(ALL_TOOLS)


# =========================
# State
# =========================

def merge_results(existing, new):
    """Combine results returned by different tool nodes."""
    return existing + new


class UtilityState(TypedDict):
    user_query: str
    tool_calls: list[dict]
    tool_results: Annotated[list[dict], merge_results]


# =========================
# Utility AI Agent
# =========================

def utility_agent(user_input: str):
    """Select tools, execute LangGraph, and generate the final answer."""

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is missing. Please add it to your .env file."
        )

    system_prompt = (
        "You are a helpful utility assistant. "
        "Use the available tools for calculations. "
        "Select all required tools for the user's request. "
        "Do not invent missing inputs. "
        "Dates must be YYYY-MM-DD. "
        "Convert user-provided units to tool units. "
        "For age without an as-of date, leave as_of_date empty. "
        "For percentages, use arithmetic expressions."
    )

    # LLM selects the required Python tools.
    selection_response = llm_with_tools.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ])

    selected_calls = selection_response.tool_calls

    # Execute selected tools through four LangGraph nodes.
    if selected_calls:

        result = utility_graph.invoke({
            "user_query": user_input,
            "tool_calls": selected_calls,
            "tool_results": []
        })

        tool_results = result["tool_results"]

    else:
        tool_results = []

    # Create the tool execution trace.
    trace = []

    for item in tool_results:
        trace.append({
            "type": "tool_call",
            "tool": item["tool"],
            "arguments": item["arguments"]
        })

        trace.append({
            "type": "tool_result",
            "tool": item["tool"],
            "result": item["result"]
        })

    # Generate final answer using tool results.
    if tool_results:

        final_prompt = f"""
User Question:
{user_input}

Tool Results:
{json.dumps(tool_results, indent=2)}

Generate a clear final answer using the tool results.
Do not change calculated values.
"""

        response = llm.invoke([
            SystemMessage(
                content="You are a helpful utility assistant."
            ),
            HumanMessage(content=final_prompt)
        ])

        final_answer = response.content

    else:
        final_answer = selection_response.content

    return {
        "answer": (
            final_answer
            if isinstance(final_answer, str)
            else str(final_answer)
        ),
        "trace": trace
    }


# =========================
# Tool Nodes
# =========================

def age_tool_node(state: UtilityState):
    """Execute the age calculation tool."""

    tool_call = state["tool_calls"][0]
    result = calculate_age.invoke(tool_call["args"])

    return {
        "tool_results": [{
            "tool": tool_call["name"],
            "arguments": tool_call["args"],
            "result": str(result)
        }]
    }


def bmi_tool_node(state: UtilityState):
    """Execute the BMI calculation tool."""

    tool_call = state["tool_calls"][0]
    result = calculate_bmi.invoke(tool_call["args"])

    return {
        "tool_results": [{
            "tool": tool_call["name"],
            "arguments": tool_call["args"],
            "result": str(result)
        }]
    }


def date_tool_node(state: UtilityState):
    """Execute the date difference tool."""

    tool_call = state["tool_calls"][0]
    result = calculate_date_difference.invoke(tool_call["args"])

    return {
        "tool_results": [{
            "tool": tool_call["name"],
            "arguments": tool_call["args"],
            "result": str(result)
        }]
    }


def calculator_tool_node(state: UtilityState):
    """Execute the general calculator tool."""

    tool_call = state["tool_calls"][0]
    result = calculate_calculator.invoke(tool_call["args"])

    return {
        "tool_results": [{
            "tool": tool_call["name"],
            "arguments": tool_call["args"],
            "result": str(result)
        }]
    }


# =========================
# Conditional Routing
# =========================

TOOL_NODE_NAMES = {
    "calculate_age": "age_tool",
    "calculate_bmi": "bmi_tool",
    "calculate_date_difference": "date_tool",
    "calculate_calculator": "calculator_tool"
}


def route_tools(state: UtilityState):
    """Send each selected tool call to its corresponding graph node."""

    return [
        Send(
            TOOL_NODE_NAMES[tool_call["name"]],
            {
                "user_query": state["user_query"],
                "tool_calls": [tool_call],
                "tool_results": []
            }
        )
        for tool_call in state["tool_calls"]
    ]


# =========================
# Build Graph
# =========================

graph = StateGraph(UtilityState)

graph.add_node("age_tool", age_tool_node)
graph.add_node("bmi_tool", bmi_tool_node)
graph.add_node("date_tool", date_tool_node)
graph.add_node("calculator_tool", calculator_tool_node)

graph.add_conditional_edges(START, route_tools)

graph.add_edge("age_tool", END)
graph.add_edge("bmi_tool", END)
graph.add_edge("date_tool", END)
graph.add_edge("calculator_tool", END)

utility_graph = graph.compile()


# =========================
# Function for FastAPI
# =========================

def run_utility_agent(user_input: str):
    """Run the Utility AI Agent."""
    return utility_agent(user_input)




"""Minimal LangGraph agent: START -> agent -> tools (if needed) -> agent -> END."""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from tools import ALL_TOOLS

load_dotenv()

SYSTEM_PROMPT = (
    "You are a helpful utility assistant. Use tools for calculations instead of doing "
    "arithmetic yourself. Use multiple tools when necessary. Ask for missing inputs "
    "rather than inventing them. Dates must be YYYY-MM-DD. Convert user-provided units "
    "to tool units. For age without an as-of date, leave as_of_date empty. "
    "BMI categories apply to adults and are not medical diagnoses. "
    "For percentages, calculate e.g. 15% of 200 as 15/100*200."
)


def build_graph():
    """Create and compile one LangGraph workflow with an LLM and four tools."""
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: MessagesState) -> dict:
        """Ask the LLM to answer or choose a tool; append its AIMessage."""
        response = llm_with_tools.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
        return {"messages": [response]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(ALL_TOOLS))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    return workflow.compile()


def run_agent(question: str) -> dict:
    """Run the graph once and return the answer and a tool execution trace."""
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

    graph = build_graph()
    result = graph.invoke({"messages": [HumanMessage(content=question)]}, config={"recursion_limit": 20})
    trace = []
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            for call in message.tool_calls:
                trace.append({"type": "tool_call", "tool": call["name"], "arguments": call["args"]})
        elif isinstance(message, ToolMessage):
            trace.append({"type": "tool_result", "tool": message.name, "result": str(message.content)})

    final = result["messages"][-1].content
    return {"answer": final if isinstance(final, str) else str(final), "trace": trace}

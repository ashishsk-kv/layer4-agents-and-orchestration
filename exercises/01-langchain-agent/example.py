"""
DEMO: LangChain Agent Building Blocks
======================================
Run this BEFORE starting the exercise. It walks through each concept
one at a time so you can see how the pieces fit together.

Run with: python example.py
"""

from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

llm = ChatOpenAI(model="gpt-4o", temperature=0)


def demo_1_basic_llm_call():
    """A plain LLM call — no tools, no agent. Just input → output."""
    print("=" * 60)
    print("DEMO 1: Basic LLM Call")
    print("=" * 60)

    response = llm.invoke([
        ("system", "You are a helpful assistant. Keep answers under 2 sentences."),
        ("user", "What is Python?"),
    ])

    print(f"Response: {response.content}")
    print(f"Tokens used: {response.usage_metadata}")
    print()


def demo_2_tool_definition():
    """How to turn any Python function into a tool the LLM can call."""
    print("=" * 60)
    print("DEMO 2: Defining Tools with @tool")
    print("=" * 60)

    @tool
    def get_current_time() -> str:
        """Return the current date and time."""
        return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

    @tool
    def multiply(a: float, b: float) -> str:
        """Multiply two numbers together."""
        return str(a * b)

    # Tools are just functions — you can call them directly
    print(f"get_current_time(): {get_current_time.invoke({})}")
    print(f"multiply(7, 6):     {multiply.invoke({'a': 7, 'b': 6})}")

    # What the LLM sees: name, description, and parameter schema
    print(f"\nTool schema for 'multiply':")
    print(f"  Name:        {multiply.name}")
    print(f"  Description: {multiply.description}")
    print(f"  Args:        {multiply.args_schema.model_json_schema()}")
    print()


def demo_3_tavily_search():
    """How Tavily web search works — the tool your agent will use."""
    print("=" * 60)
    print("DEMO 3: Tavily Web Search")
    print("=" * 60)

    tavily = TavilySearch(max_results=2)
    response = tavily.invoke("latest Python version 2026")

    print(f"Response type: {type(response).__name__}")
    print(f"Top-level keys: {list(response.keys())}")
    print(f"Number of results: {len(response['results'])}")
    print()

    for i, r in enumerate(response["results"], 1):
        print(f"  Result {i}:")
        print(f"    URL:     {r['url']}")
        print(f"    Title:   {r['title']}")
        print(f"    Content: {r['content'][:150]}...")
        print()


def demo_4_simple_agent():
    """Wire an LLM + tools into an agent that reasons and acts."""
    print("=" * 60)
    print("DEMO 4: A Simple Agent (LLM + Tools)")
    print("=" * 60)

    tavily = TavilySearch(max_results=2)

    @tool
    def search_web(query: str) -> str:
        """Search the web for current information on any topic."""
        response = tavily.invoke(query)
        return "\n".join(
            f"- {r['content'][:200]}" for r in response["results"]
        )

    @tool
    def calculate(expression: str) -> str:
        """Evaluate a math expression like '2 + 2' or '100 / 3'."""
        try:
            return str(eval(expression, {"__builtins__": {}}, {}))
        except Exception as e:
            return f"Error: {e}"

    agent = create_agent(
        llm,
        tools=[search_web, calculate],
        system_prompt="You are a helpful assistant. Use tools when needed.",
    )

    query = "What is the population of Brazil? Divide it by 100."
    print(f"Query: {query}\n")

    # Stream so we can see each step of the ReAct loop
    for event in agent.stream(
        {"messages": [("user", query)]}, stream_mode="values"
    ):
        if event.get("messages"):
            msg = event["messages"][-1]
            if msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"  🔧 Tool call: {tc['name']}({tc['args']})")
            elif msg.type == "tool":
                print(f"  📎 Tool result: {msg.content[:150]}")
            elif msg.type == "ai" and msg.content:
                print(f"\n  ✅ Final answer: {msg.content}")
    print()


if __name__ == "__main__":
    print()
    print("Layer 4 Workshop — LangChain Agent Demo")
    print("This demo walks through each building block one by one.")
    print()

    demo_1_basic_llm_call()
    demo_2_tool_definition()
    demo_3_tavily_search()
    demo_4_simple_agent()

    print("=" * 60)
    print("That's it! Now open starter.py and build your own agent.")
    print("=" * 60)

"""
Exercise 1: LangChain Chains & Agents (SOLUTION)
==================================================
Part A — LCEL chain (deterministic multi-step pipeline).
Part B — ReAct agent with tools.

Run with: python solution.py
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import create_agent

# ============================================================
# STEP 1: Environment & LLM Setup
# ============================================================

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

llm = ChatOpenAI(model="gpt-4o", temperature=0)
parser = StrOutputParser()


# ============================================================
# PART A: BUILD A LANGCHAIN CHAIN
# ============================================================


# ============================================================
# STEP 2: Simple Chain — prompt | llm | parser
# ============================================================

explain_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful teacher. Explain topics clearly in 2-3 sentences."),
    ("user", "Explain {topic}"),
])
explain_chain = explain_prompt | llm | parser


# ============================================================
# PART B: BUILD A LANGCHAIN AGENT
# ============================================================


# ============================================================
# STEP 4a: Web Search Tool
# ============================================================

tavily_search = TavilySearch(max_results=3)

@tool
def search_web(query: str) -> str:
    """Search the web for current information on any topic. Use this when you need up-to-date facts, news, or data."""
    response = tavily_search.invoke(query)
    formatted = []
    for r in response["results"]:
        formatted.append(f"- {r['content'][:300]}")
    return "\n".join(formatted) if formatted else "No results found."


# ============================================================
# STEP 4b: Calculator Tool
# ============================================================

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. Input should be a valid math expression like '2 + 2' or '100 * 3.14'."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


# ============================================================
# STEP 4c: Wikipedia Tool
# ============================================================

wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
wiki_runner = WikipediaQueryRun(api_wrapper=wiki_api)

@tool
def wiki_search(query: str) -> str:
    """Look up a topic on Wikipedia for encyclopedic information and historical facts."""
    return wiki_runner.invoke(query)


# ============================================================
# STEP 5: Create the Agent
# ============================================================

system_prompt = (
    "You are a helpful research assistant. You have access to web search, "
    "a calculator, and Wikipedia. Use your tools to find accurate, up-to-date "
    "information. Always show your reasoning and cite your sources when possible. "
    "If a question requires multiple steps, break it down and solve each part."
)

tools = [search_web, calculate, wiki_search]
agent = create_agent(llm, tools, system_prompt=system_prompt)


# ============================================================
# STEP 6: Test the Agent
# ============================================================

def run_query(query: str):
    """Run a query through the agent and print the result."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    result = agent.invoke({"messages": [("user", query)]})
    final_message = result["messages"][-1]
    print(f"\nAgent Response:\n{final_message.content}")


# ============================================================
# STEP 7: Custom Tool — Current Time
# ============================================================

@tool
def get_current_time() -> str:
    """Get the current date and time. Use this when the user asks about today's date or the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools_extended = [search_web, calculate, wiki_search, get_current_time]
agent_extended = create_agent(llm, tools_extended, system_prompt=system_prompt)


# ============================================================
# STEP 8: Observe the ReAct Loop
# ============================================================

def run_query_streaming(query: str):
    """Run a query with streaming to observe the ReAct loop step by step."""
    print(f"\n{'='*60}")
    print(f"Query (streaming): {query}")
    print('='*60)

    for event in agent.stream({"messages": [("user", query)]}, stream_mode="values"):
        if event.get("messages"):
            last = event["messages"][-1]
            content_preview = last.content[:300] if last.content else "(no text content)"
            print(f"\n  [{last.type}] {content_preview}")

            if hasattr(last, "tool_calls") and last.tool_calls:
                for tc in last.tool_calls:
                    print(f"    -> Calling tool: {tc['name']}({tc['args']})")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 1: LangChain Chains & Agents (SOLUTION)")
    print("=" * 60)

    # ---- Part A: Chains ----
    print("\n\n--- PART A: CHAINS ---\n")

    # Step 2: Simple chain
    result = explain_chain.invoke({"topic": "quantum computing"})
    print(f"Simple chain result:\n{result}\n")

    # ---- Part B: Agent ----
    print("\n\n--- PART B: AGENT ---\n")

    # Step 6: Basic queries
    run_query("What is the current population of Japan?")

    run_query(
        "What is the population of Germany? "
        "Multiply it by 3 and tell me the result."
    )

    run_query("Give me a brief summary of the Theory of Relativity from Wikipedia.")

    # Step 7: Custom tool test
    print("\n\n--- Testing with extended agent (includes get_current_time) ---")
    result = agent_extended.invoke(
        {"messages": [("user", "What is today's date and time?")]}
    )
    print(f"\nAgent Response:\n{result['messages'][-1].content}")

    # Step 8: Streaming to observe ReAct loop
    run_query_streaming(
        "Search for the GDP of India, then calculate what 15% of it would be."
    )

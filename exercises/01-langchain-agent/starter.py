"""
Exercise 1: LangChain Agent — Research Assistant
=================================================
Build a ReAct agent with web search, calculator, and Wikipedia tools.

Instructions: Fill in each TODO section. Run with: python starter.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents import create_agent

# ============================================================
# STEP 1: Environment & LLM Setup
# ============================================================

# Load .env from the repo root (two levels up from this file)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# TODO: Initialize the ChatOpenAI model
# - Use model="gpt-4o"
# - Set temperature=0 for deterministic outputs
#
# llm = ChatOpenAI(...)
llm = None  # <-- Replace this line


# ============================================================
# STEP 2a: Web Search Tool
# ============================================================

# TODO: Create a web search tool using TavilySearch
# - Initialize TavilySearch with max_results=3
# - Create a function decorated with @tool that:
#   1. Takes a search query (str) as input
#   2. Calls tavily_search.invoke(query) — returns a dict with a "results" key
#   3. Iterates over response["results"] (list of dicts with "content", "url", etc.)
#   4. Formats the results into a readable string
#
# Example:
#   tavily_search = TavilySearch(max_results=3)
#
#   @tool
#   def search_web(query: str) -> str:
#       """Search the web for current information on any topic."""
#       response = tavily_search.invoke(query)
#       formatted = [r["content"][:300] for r in response["results"]]
#       ...

# Your code here:


# ============================================================
# STEP 2b: Calculator Tool
# ============================================================

# TODO: Create a calculator tool
# - Decorate with @tool
# - Takes a math expression as a string (e.g., "2 + 2", "100 * 3.14")
# - Evaluates it and returns the result as a string
# - Wrap in try/except to handle invalid expressions
#
# Example:
#   @tool
#   def calculate(expression: str) -> str:
#       """Evaluate a mathematical expression. Input should be a valid math expression like '2 + 2' or '100 * 3.14'."""
#       ...

# Your code here:


# ============================================================
# STEP 2c: Wikipedia Tool
# ============================================================

# TODO: Create a Wikipedia search tool
# - Initialize WikipediaAPIWrapper with top_k_results=1, doc_content_chars_max=1000
# - Initialize WikipediaQueryRun with the wrapper
# - Create a function decorated with @tool that:
#   1. Takes a search term (str)
#   2. Returns the Wikipedia summary
#
# Example:
#   wiki_api = WikipediaAPIWrapper(...)
#   wiki_runner = WikipediaQueryRun(api_wrapper=wiki_api)
#
#   @tool
#   def wiki_search(query: str) -> str:
#       """Look up a topic on Wikipedia for encyclopedic information."""
#       ...

# Your code here:


# ============================================================
# STEP 3: Create the Agent
# ============================================================

# TODO: Assemble the agent
# 1. Create a list of your tools: [search_web, calculate, wiki_search]
# 2. Define a system prompt string that tells the agent who it is and how to behave
#    Example: "You are a helpful research assistant. Use your tools to find
#    accurate information. Always show your reasoning."
# 3. Create the agent using create_agent(llm, tools, system_prompt=system_prompt)
#
# agent = create_agent(...)

tools = []  # <-- Add your tools here
system_prompt = ""  # <-- Write your system prompt here
agent = None  # <-- Replace this line


# ============================================================
# STEP 4: Test the Agent
# ============================================================

def run_query(query: str):
    """Run a query through the agent and print the result."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    if agent is None:
        print("ERROR: Agent is not initialized. Complete the TODOs above first.")
        return

    result = agent.invoke({"messages": [("user", query)]})
    final_message = result["messages"][-1]
    print(f"\nAgent Response:\n{final_message.content}")


# ============================================================
# STEP 5: Add a Custom Tool (Bonus)
# ============================================================

# TODO (Bonus): Create your own tool!
# Ideas:
#   - get_current_time: returns the current date and time
#   - reverse_string: reverses a given string
#   - count_words: counts words in a text
#
# Don't forget to add it to the tools list and recreate the agent.

# Your code here:


# ============================================================
# STEP 6: Observe the ReAct Loop
# ============================================================

def run_query_streaming(query: str):
    """Run a query with streaming to observe the ReAct loop step by step."""
    print(f"\n{'='*60}")
    print(f"Query (streaming): {query}")
    print('='*60)

    if agent is None:
        print("ERROR: Agent is not initialized. Complete the TODOs above first.")
        return

    for event in agent.stream({"messages": [("user", query)]}, stream_mode="values"):
        if event.get("messages"):
            last = event["messages"][-1]
            # Show message type and a preview of the content
            content_preview = last.content[:300] if last.content else "(no text content)"
            print(f"\n  [{last.type}] {content_preview}")

            # If it's a tool call, show which tool is being called
            if hasattr(last, "tool_calls") and last.tool_calls:
                for tc in last.tool_calls:
                    print(f"    -> Calling tool: {tc['name']}({tc['args']})")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 1: LangChain Agent")
    print("=" * 60)

    # Step 4: Test with these queries
    run_query("What is the current population of Japan?")

    run_query(
        "What is the population of Germany? "
        "Multiply it by 3 and tell me the result."
    )

    run_query("Give me a brief summary of the Theory of Relativity from Wikipedia.")

    # Step 6: Uncomment to see the ReAct loop in action
    # run_query_streaming(
    #     "Search for the GDP of India, then calculate what 15% of it would be."
    # )

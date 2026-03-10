"""
Exercise 3 — Part A: LangSmith Tracing
========================================
Learn to trace LangChain calls automatically and add custom
spans with @traceable.

Instructions: Fill in each TODO section. Run with: python starter_tracing.py
Then check your traces at https://smith.langchain.com
"""

from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langsmith import traceable

# ============================================================
# Environment Setup
# ============================================================

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ============================================================
# STEP 1: Automatic Tracing with a Simple Chain
# ============================================================

# TODO: Create a simple LangChain chain and invoke it.
# Traces are sent automatically when LANGSMITH_TRACING=true.
#
# 1. Initialize a ChatOpenAI model (gpt-4o, temperature=0)
# 2. Create a ChatPromptTemplate with a system message and user message
#    Example:
#      prompt = ChatPromptTemplate.from_messages([
#          ("system", "You are a helpful assistant that gives concise answers."),
#          ("user", "{question}"),
#      ])
# 3. Create an output parser: StrOutputParser()
# 4. Chain them: chain = prompt | llm | parser
# 5. Invoke: result = chain.invoke({"question": "What is LangSmith?"})
# 6. Print the result
#
# After running, go to https://smith.langchain.com → layer4-workshop project
# and find your trace. Click into it to see the prompt, response, tokens.

def step1_automatic_tracing():
    print("\n--- Step 1: Automatic Tracing ---")

    # Your code here:
    pass


# ============================================================
# STEP 2: Custom Traces with @traceable
# ============================================================

# TODO: Create a multi-step pipeline with custom tracing.
# The @traceable decorator makes any function appear as a span in LangSmith.
#
# 1. Create a @traceable function called `research_pipeline` that:
#    a. Calls a nested @traceable function `generate_query` to turn a topic
#       into a search query using the LLM
#    b. Calls a nested @traceable function `search_and_summarize` that
#       searches with Tavily and summarizes the results with the LLM
#    c. Returns the final summary
#
# 2. Use metadata to tag your traces:
#    @traceable(metadata={"exercise": "03-langsmith", "step": "2"})
#
# After running, find the trace in LangSmith. You should see a tree:
#   research_pipeline
#     ├── generate_query
#     │     └── ChatOpenAI (auto-traced)
#     └── search_and_summarize
#           ├── TavilySearch (auto-traced)
#           └── ChatOpenAI (auto-traced)

def step2_custom_tracing():
    print("\n--- Step 2: Custom Traces with @traceable ---")

    # Your code here:
    # Define @traceable functions, then call the pipeline
    pass


# ============================================================
# STEP 3: Trace a ReAct Agent
# ============================================================

# TODO: Build a simple ReAct agent and run it, then observe the trace.
#
# 1. Create a ChatOpenAI model
# 2. Create at least one tool (e.g., web search with Tavily)
# 3. Create an agent with create_agent(model, tools)
# 4. Invoke with a query that requires tool use
# 5. Check LangSmith to see the full ReAct loop trace:
#    - Each LLM reasoning step
#    - Each tool call with inputs/outputs
#    - Total execution time and token count
#
# The beauty here: you don't need to add ANY tracing code.
# LangChain + LangSmith handles it automatically.

def step3_trace_agent():
    print("\n--- Step 3: Tracing a ReAct Agent ---")

    # Your code here:
    pass


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 3, Part A: LangSmith Tracing")
    print("=" * 60)
    print("Make sure LANGSMITH_TRACING=true in your .env file!")
    print("View traces at: https://smith.langchain.com")
    print("=" * 60)

    step1_automatic_tracing()
    step2_custom_tracing()
    step3_trace_agent()

    print("\n" + "=" * 60)
    print("Done! Go to https://smith.langchain.com to view your traces.")
    print("Look for the 'layer4-workshop' project in the left sidebar.")
    print("=" * 60)

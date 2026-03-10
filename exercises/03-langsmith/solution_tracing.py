"""
Exercise 3 — Part A: LangSmith Tracing (SOLUTION)
===================================================
Automatic tracing, custom spans with @traceable, and agent tracing.

Run with: python solution_tracing.py
Then check traces at https://smith.langchain.com
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

def step1_automatic_tracing():
    print("\n--- Step 1: Automatic Tracing ---")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that gives concise answers."),
        ("user", "{question}"),
    ])
    parser = StrOutputParser()

    chain = prompt | llm | parser
    result = chain.invoke({"question": "What is LangSmith and why is it useful?"})

    print(f"Response: {result[:200]}")
    print("→ Check LangSmith UI for the trace of this chain call.")


# ============================================================
# STEP 2: Custom Traces with @traceable
# ============================================================

def step2_custom_tracing():
    print("\n--- Step 2: Custom Traces with @traceable ---")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tavily = TavilySearch(max_results=2)

    @traceable(metadata={"exercise": "03-langsmith", "step": "2"})
    def generate_query(topic: str) -> str:
        """Turn a broad topic into a focused search query."""
        response = llm.invoke([
            ("system", "Generate a concise web search query for researching the following topic."),
            ("user", topic),
        ])
        return response.content

    @traceable(metadata={"exercise": "03-langsmith", "step": "2"})
    def search_and_summarize(query: str) -> str:
        """Search the web and summarize findings."""
        response = tavily.invoke(query)
        context = "\n".join([r["content"][:300] for r in response["results"]])
        response = llm.invoke([
            ("system", "Summarize the following search results into 2-3 key points."),
            ("user", context),
        ])
        return response.content

    @traceable(
        run_type="chain",
        metadata={"exercise": "03-langsmith", "step": "2", "pipeline": "research"},
    )
    def research_pipeline(topic: str) -> str:
        """Full research pipeline: topic → query → search → summary."""
        query = generate_query(topic)
        print(f"  Generated query: {query}")
        summary = search_and_summarize(query)
        return summary

    result = research_pipeline("AI agents in software engineering 2026")
    print(f"Summary: {result[:300]}")
    print("→ Check LangSmith for nested spans: research_pipeline → generate_query + search_and_summarize")


# ============================================================
# STEP 3: Trace a ReAct Agent
# ============================================================

def step3_trace_agent():
    print("\n--- Step 3: Tracing a ReAct Agent ---")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tavily = TavilySearch(max_results=2)

    @tool
    def search_web(query: str) -> str:
        """Search the web for current information."""
        response = tavily.invoke(query)
        return "\n".join([f"- {r['content'][:200]}" for r in response["results"]])

    @tool
    def calculate(expression: str) -> str:
        """Evaluate a math expression like '2 + 2' or '100 * 3.14'."""
        try:
            return str(eval(expression, {"__builtins__": {}}, {}))
        except Exception as e:
            return f"Error: {e}"

    agent = create_agent(
        llm,
        [search_web, calculate],
        system_prompt="You are a helpful research assistant. Use tools when needed.",
    )

    result = agent.invoke({
        "messages": [("user", "What is the GDP of Japan in USD? Calculate 5% of it.")]
    })

    final = result["messages"][-1].content
    print(f"Agent response: {final[:300]}")
    print("→ Check LangSmith for the full ReAct loop: each reasoning step, tool call, and observation.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 3, Part A: LangSmith Tracing (SOLUTION)")
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

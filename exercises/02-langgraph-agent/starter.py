"""
Exercise 2: LangGraph Agent — Blog Writer Workflow
====================================================
Build a stateful multi-step workflow that plans, researches, writes,
and reviews a blog post using LangGraph.

Instructions: Fill in each TODO section. Run with: python starter.py
"""

import operator
from pathlib import Path
from typing import Annotated, TypedDict

from IPython.display import display
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

# ============================================================
# Environment Setup
# ============================================================

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

llm = ChatOpenAI(model="gpt-4o", temperature=0)
tavily_search = TavilySearch(max_results=3)


# ============================================================
# STEP 1: Define the State
# ============================================================

# TODO: Define the BlogWriterState TypedDict
# Fields:
#   topic: str
#   plan: str
#   research: str
#   draft: str
#   feedback: str
#   final_article: str
#   revision_count: int
#
# Example:
#   class BlogWriterState(TypedDict):
#       topic: str
#       plan: str
#       ...

class BlogWriterState(TypedDict):
    pass  # <-- Replace with your fields


# ============================================================
# STEP 2: Planner Node
# ============================================================

# TODO: Create the planner node function
# - Takes state: BlogWriterState
# - Gets the topic from state["topic"]
# - Asks the LLM to create a structured blog outline with:
#   * Title
#   * 3-5 sections with brief descriptions
#   * Key points to cover in each section
# - Returns {"plan": outline_text}
#
# Hint: Use llm.invoke() with a list of messages:
#   response = llm.invoke([
#       ("system", "You are a content strategist..."),
#       ("user", f"Create an outline for: {topic}")
#   ])
#   return {"plan": response.content}

def plan_node(state: BlogWriterState) -> dict:
    pass  # <-- Replace with your implementation


# ============================================================
# STEP 3: Researcher Node
# ============================================================

# TODO: Create the researcher node function
# - Takes state: BlogWriterState
# - Gets the plan from state["plan"]
# - Uses tavily_search.invoke() to search for relevant info
# - Compile search results into a single research string
# - Returns {"research": compiled_research}
#
# Hint: Search for the overall topic or key sections from the plan
#   response = tavily_search.invoke(state["topic"])
#   research = "\n".join([r["content"][:300] for r in response["results"]])

def research_node(state: BlogWriterState) -> dict:
    pass  # <-- Replace with your implementation


# ============================================================
# STEP 4: Writer Node
# ============================================================

# TODO: Create the writer node function
# - Takes state: BlogWriterState
# - Builds a prompt using: topic, plan, research
# - If state["feedback"] is not empty, include it so the LLM addresses the feedback
# - Asks the LLM to write the blog post
# - Returns {"draft": article_text, "revision_count": state["revision_count"] + 1}
#
# Hint: Build a detailed prompt:
#   prompt = f"""Write a blog post on: {state['topic']}
#   Outline: {state['plan']}
#   Research: {state['research']}
#   {"Previous feedback to address: " + state['feedback'] if state.get('feedback') else ""}
#   """

def write_node(state: BlogWriterState) -> dict:
    pass  # <-- Replace with your implementation


# ============================================================
# STEP 5: Reviewer Node + Routing
# ============================================================

# TODO: Create the reviewer node function
# - Takes state: BlogWriterState
# - Asks the LLM to evaluate the draft for:
#   * Accuracy and relevance
#   * Structure and flow
#   * Completeness
# - The LLM should respond starting with either:
#   "APPROVED" — if the draft is good
#   "NEEDS_REVISION:" — followed by specific feedback
# - If approved: return {"final_article": state["draft"], "feedback": ""}
# - If needs revision: return {"feedback": feedback_text}

def review_node(state: BlogWriterState) -> dict:
    pass  # <-- Replace with your implementation


# TODO: Create the routing function
# - Takes state: BlogWriterState
# - Returns "writer" if:
#   * state["feedback"] is not empty (needs revision)
#   * AND state["revision_count"] < 2 (haven't exceeded max revisions)
# - Returns "human_approval" otherwise
#
# def should_revise(state: BlogWriterState) -> str:
#     ...

def should_revise(state: BlogWriterState) -> str:
    pass  # <-- Replace with your implementation


# ============================================================
# STEP 6: Human Approval + Graph Assembly
# ============================================================

# TODO: Create the human approval node
# - Uses interrupt() to pause the workflow
# - The interrupt payload should contain the final article for review
# - After resuming, marks the article as approved
#
# def human_approval_node(state: BlogWriterState) -> dict:
#     answer = interrupt({"article": state["final_article"], "question": "Approve this article? (yes/no)"})
#     if answer.lower() == "yes":
#         return {"final_article": state["final_article"]}
#     return {"feedback": "Human rejected: " + answer, "final_article": ""}

def human_approval_node(state: BlogWriterState) -> dict:
    pass  # <-- Replace with your implementation


# TODO: Build the graph
# 1. Create a StateGraph(BlogWriterState)
# 2. Add nodes: "planner", "researcher", "writer", "reviewer", "human_approval"
# 3. Add edges:
#    - START -> "planner"
#    - "planner" -> "researcher"
#    - "researcher" -> "writer"
#    - "writer" -> "reviewer"
#    - Conditional: "reviewer" -> should_revise -> {"writer": "writer", "human_approval": "human_approval"}
#    - "human_approval" -> END
# 4. Compile with MemorySaver checkpointer

# Your code here:
graph = None  # <-- Replace with your compiled graph


# ============================================================
# STEP 7: Visualize the Graph
# ============================================================

def visualize():
    """Print the graph structure as Mermaid text."""
    if graph is None:
        print("ERROR: Graph is not initialized. Complete the TODOs above first.")
        return
    print("\nGraph structure (Mermaid):")
    from IPython.display import Image, display
    display(Image(graph.get_graph().draw_mermaid_png()))


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 2: LangGraph Agent")
    print("=" * 60)

    if graph is None:
        print("ERROR: Graph is not initialized. Complete the TODOs above first.")
        exit(1)

    # Visualize the graph
    visualize()

    # Run the workflow
    config = {"configurable": {"thread_id": "workshop-demo-1"}}
    topic = "The Impact of AI Agents on Software Engineering in 2026"

    print(f"\nStarting blog writer workflow for topic:")
    print(f"  '{topic}'")
    print("=" * 60)

    initial_state = {
        "topic": topic,
        "plan": "",
        "research": "",
        "draft": "",
        "feedback": "",
        "final_article": "",
        "revision_count": 0,
    }

    # First invocation — will run until it hits the interrupt at human_approval
    result = graph.invoke(initial_state, config)

    # Check if we hit an interrupt
    snapshot = graph.get_state(config)
    if snapshot.next:
        print("\n" + "=" * 60)
        print("WORKFLOW PAUSED — Human approval required")
        print("=" * 60)

        # Show the article for review
        print("\n--- Draft Article ---")
        article = result.get("final_article", result.get("draft", ""))
        print(article[:1000] + "..." if len(article) > 1000 else article)

        # Simulate human approval
        print("\n[Simulating human approval: 'yes']")
        result = graph.invoke(Command(resume="yes"), config)

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print("\n--- Final Article ---")
    print(result.get("final_article", "(no final article produced)")[:2000])

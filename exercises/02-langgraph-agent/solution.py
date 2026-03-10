"""
Exercise 2: LangGraph Agent — Blog Writer Workflow (SOLUTION)
==============================================================
A stateful multi-step workflow that plans, researches, writes,
and reviews a blog post using LangGraph.

Run with: python solution.py
"""

import operator
from pathlib import Path
from typing import Annotated, TypedDict

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

class BlogWriterState(TypedDict):
    topic: str
    plan: str
    research: str
    draft: str
    feedback: str
    final_article: str
    revision_count: int


# ============================================================
# STEP 2: Planner Node
# ============================================================

def plan_node(state: BlogWriterState) -> dict:
    topic = state["topic"]
    response = llm.invoke([
        (
            "system",
            "You are a content strategist. Create a structured blog post outline. "
            "Include a compelling title, 3-5 sections with brief descriptions, and "
            "key points to cover in each section. Format it clearly with markdown headers."
        ),
        ("user", f"Create a detailed outline for a blog post about: {topic}"),
    ])
    print(f"  [Planner] Generated outline ({len(response.content)} chars)")
    return {"plan": response.content}


# ============================================================
# STEP 3: Researcher Node
# ============================================================

def research_node(state: BlogWriterState) -> dict:
    topic = state["topic"]
    response = tavily_search.invoke(topic)
    results = response["results"]
    research_parts = []
    for r in results:
        research_parts.append(f"Source: {r.get('url', 'N/A')}\n{r['content'][:500]}")
    compiled = "\n\n---\n\n".join(research_parts)
    print(f"  [Researcher] Found {len(results)} sources ({len(compiled)} chars)")
    return {"research": compiled}


# ============================================================
# STEP 4: Writer Node
# ============================================================

def write_node(state: BlogWriterState) -> dict:
    feedback_section = ""
    if state.get("feedback"):
        feedback_section = (
            f"\n\nIMPORTANT — Address this feedback from the reviewer:\n"
            f"{state['feedback']}"
        )

    response = llm.invoke([
        (
            "system",
            "You are a skilled technical blog writer. Write engaging, informative "
            "content that is well-structured and accessible to software engineers. "
            "Use the provided outline and research to write a complete blog post."
        ),
        (
            "user",
            f"Write a blog post on: {state['topic']}\n\n"
            f"Outline:\n{state['plan']}\n\n"
            f"Research:\n{state['research']}"
            f"{feedback_section}"
        ),
    ])
    revision = state.get("revision_count", 0) + 1
    print(f"  [Writer] Wrote draft v{revision} ({len(response.content)} chars)")
    return {"draft": response.content, "revision_count": revision}


# ============================================================
# STEP 5: Reviewer Node + Routing
# ============================================================

def review_node(state: BlogWriterState) -> dict:
    response = llm.invoke([
        (
            "system",
            "You are an editorial reviewer. Evaluate the following blog post draft "
            "for accuracy, structure, completeness, and engagement.\n\n"
            "Respond with EXACTLY one of:\n"
            "- 'APPROVED' if the article is ready for publication\n"
            "- 'NEEDS_REVISION: <specific feedback>' if improvements are needed\n\n"
            "Be constructive but maintain a high quality bar."
        ),
        ("user", f"Review this draft:\n\n{state['draft']}"),
    ])

    review_text = response.content.strip()
    print(f"  [Reviewer] Verdict: {review_text[:80]}...")

    if review_text.upper().startswith("APPROVED"):
        return {"final_article": state["draft"], "feedback": ""}

    feedback = review_text.replace("NEEDS_REVISION:", "").strip()
    return {"feedback": feedback}


def should_revise(state: BlogWriterState) -> str:
    if state.get("feedback") and state.get("revision_count", 0) < 2:
        print(f"  [Router] Sending back for revision (attempt {state['revision_count']}/2)")
        return "writer"
    print("  [Router] Moving to human approval")
    return "human_approval"


# ============================================================
# STEP 6: Human Approval Node + Graph Assembly
# ============================================================

def human_approval_node(state: BlogWriterState) -> dict:
    answer = interrupt({
        "article_preview": state["final_article"][:500] + "...",
        "question": "Approve this article for publication? (yes/no)",
    })
    if answer.lower() == "yes":
        return {"final_article": state["final_article"]}
    return {"feedback": f"Human rejected: {answer}", "final_article": ""}


# Build the graph
builder = StateGraph(BlogWriterState)

builder.add_node("planner", plan_node)
builder.add_node("researcher", research_node)
builder.add_node("writer", write_node)
builder.add_node("reviewer", review_node)
builder.add_node("human_approval", human_approval_node)

builder.add_edge(START, "planner")
builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "reviewer")
builder.add_conditional_edges("reviewer", should_revise, {
    "writer": "writer",
    "human_approval": "human_approval",
})
builder.add_edge("human_approval", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# ============================================================
# STEP 7: Visualize the Graph
# ============================================================

def visualize():
    """Print the graph structure as Mermaid text."""
    print("\nGraph structure (Mermaid):")
    print(graph.get_graph().draw_mermaid())


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 2: LangGraph Agent (SOLUTION)")
    print("=" * 60)

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

    # First invocation — runs until interrupt at human_approval
    result = graph.invoke(initial_state, config)

    # Check if we hit an interrupt
    snapshot = graph.get_state(config)
    if snapshot.next:
        print("\n" + "=" * 60)
        print("WORKFLOW PAUSED — Human approval required")
        print("=" * 60)

        article = result.get("final_article", result.get("draft", ""))
        print("\n--- Draft Article Preview ---")
        print(article[:1000] + "..." if len(article) > 1000 else article)

        # Simulate human approval
        print("\n[Simulating human approval: 'yes']")
        result = graph.invoke(Command(resume="yes"), config)

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETE")
    print("=" * 60)
    print("\n--- Final Article ---")
    final = result.get("final_article", "(no final article produced)")
    print(final[:2000] + "..." if len(final) > 2000 else final)

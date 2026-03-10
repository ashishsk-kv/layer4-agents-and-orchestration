"""
DEMO: LangGraph Building Blocks
=================================
Run this BEFORE starting the exercise. It builds up from a minimal
2-node graph to conditional routing and checkpointing, so you can
see how each LangGraph concept works in isolation.

Run with: python example.py
"""

from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

llm = ChatOpenAI(model="gpt-4o", temperature=0)


# ─────────────────────────────────────────────────────────────
def demo_1_minimal_graph():
    """The simplest possible LangGraph: two nodes in sequence."""
    print("=" * 60)
    print("DEMO 1: Minimal Graph (2 nodes)")
    print("=" * 60)

    class State(TypedDict):
        name: str
        greeting: str

    def greet(state: State) -> dict:
        return {"greeting": f"Hello, {state['name']}!"}

    def shout(state: State) -> dict:
        return {"greeting": state["greeting"].upper()}

    builder = StateGraph(State)
    builder.add_node("greet", greet)
    builder.add_node("shout", shout)
    builder.add_edge(START, "greet")
    builder.add_edge("greet", "shout")
    builder.add_edge("shout", END)

    graph = builder.compile()

    # Visualize
    print("\nGraph (Mermaid):")
    print(graph.get_graph().draw_mermaid())

    # Run
    result = graph.invoke({"name": "Workshop", "greeting": ""})
    print(f"Result: {result}")
    print()


# ─────────────────────────────────────────────────────────────
def demo_2_llm_node():
    """A node that calls an LLM to transform state."""
    print("=" * 60)
    print("DEMO 2: LLM Node")
    print("=" * 60)

    class JokeState(TypedDict):
        topic: str
        joke: str

    def write_joke(state: JokeState) -> dict:
        response = llm.invoke([
            ("system", "You are a comedian. Write a short one-liner joke."),
            ("user", f"Tell me a joke about: {state['topic']}"),
        ])
        return {"joke": response.content}

    builder = StateGraph(JokeState)
    builder.add_node("comedian", write_joke)
    builder.add_edge(START, "comedian")
    builder.add_edge("comedian", END)

    graph = builder.compile()
    result = graph.invoke({"topic": "Python programming", "joke": ""})

    print(f"Topic: {result['topic']}")
    print(f"Joke:  {result['joke']}")
    print()


# ─────────────────────────────────────────────────────────────
def demo_3_tavily_node():
    """A node that searches the web with Tavily."""
    print("=" * 60)
    print("DEMO 3: Web Search Node (Tavily)")
    print("=" * 60)

    tavily = TavilySearch(max_results=2)

    class ResearchState(TypedDict):
        query: str
        findings: str

    def research(state: ResearchState) -> dict:
        response = tavily.invoke(state["query"])
        results = response["results"]
        findings = "\n".join(
            f"- [{r['title']}] {r['content'][:150]}"
            for r in results
        )
        return {"findings": findings}

    builder = StateGraph(ResearchState)
    builder.add_node("research", research)
    builder.add_edge(START, "research")
    builder.add_edge("research", END)

    graph = builder.compile()
    result = graph.invoke({"query": "LangGraph framework 2026", "findings": ""})

    print(f"Query: {result['query']}")
    print(f"Findings:\n{result['findings']}")
    print()


# ─────────────────────────────────────────────────────────────
def demo_4_conditional_edges():
    """Conditional routing: a node decides which path to take."""
    print("=" * 60)
    print("DEMO 4: Conditional Edges (Branching)")
    print("=" * 60)

    class ReviewState(TypedDict):
        text: str
        word_count: int
        verdict: str

    def count_words(state: ReviewState) -> dict:
        count = len(state["text"].split())
        return {"word_count": count}

    def approve(state: ReviewState) -> dict:
        return {"verdict": f"Approved! ({state['word_count']} words)"}

    def reject(state: ReviewState) -> dict:
        return {"verdict": f"Too short — only {state['word_count']} words. Need at least 5."}

    def route(state: ReviewState) -> str:
        return "approve" if state["word_count"] >= 5 else "reject"

    builder = StateGraph(ReviewState)
    builder.add_node("count", count_words)
    builder.add_node("approve", approve)
    builder.add_node("reject", reject)

    builder.add_edge(START, "count")
    builder.add_conditional_edges("count", route, {
        "approve": "approve",
        "reject": "reject",
    })
    builder.add_edge("approve", END)
    builder.add_edge("reject", END)

    graph = builder.compile()

    # Visualize
    print("\nGraph (Mermaid):")
    print(graph.get_graph().draw_mermaid())

    # Test both paths
    long_text = "LangGraph makes it easy to build stateful workflows"
    short_text = "Hello world"

    r1 = graph.invoke({"text": long_text, "word_count": 0, "verdict": ""})
    print(f"Input:   '{long_text}'")
    print(f"Result:  {r1['verdict']}")
    print()

    r2 = graph.invoke({"text": short_text, "word_count": 0, "verdict": ""})
    print(f"Input:   '{short_text}'")
    print(f"Result:  {r2['verdict']}")
    print()


# ─────────────────────────────────────────────────────────────
def demo_5_checkpointing():
    """Checkpointing: persist state across invocations with thread_id."""
    print("=" * 60)
    print("DEMO 5: Checkpointing (Memory)")
    print("=" * 60)

    class CounterState(TypedDict):
        count: int

    def increment(state: CounterState) -> dict:
        new_count = state["count"] + 1
        print(f"  Incrementing: {state['count']} → {new_count}")
        return {"count": new_count}

    builder = StateGraph(CounterState)
    builder.add_node("increment", increment)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)

    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "demo-counter"}}

    # Each invoke picks up where the last one left off
    r1 = graph.invoke({"count": 0}, config)
    print(f"After call 1: count = {r1['count']}")

    r2 = graph.invoke({"count": r1["count"]}, config)
    print(f"After call 2: count = {r2['count']}")

    r3 = graph.invoke({"count": r2["count"]}, config)
    print(f"After call 3: count = {r3['count']}")

    # Different thread = fresh state
    other_config = {"configurable": {"thread_id": "different-thread"}}
    r4 = graph.invoke({"count": 0}, other_config)
    print(f"Different thread: count = {r4['count']}")
    print()


if __name__ == "__main__":
    print()
    print("Layer 4 Workshop — LangGraph Demo")
    print("This demo walks through each LangGraph concept one by one.")
    print()

    demo_1_minimal_graph()
    demo_2_llm_node()
    demo_3_tavily_node()
    demo_4_conditional_edges()
    demo_5_checkpointing()

    print("=" * 60)
    print("That's it! Now open starter.py and build the Blog Writer workflow.")
    print("=" * 60)

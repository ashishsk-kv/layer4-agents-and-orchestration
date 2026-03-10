# Day 1: Agents & Orchestration

## What is an AI Agent?

An agent is a system that uses an LLM as its reasoning engine to decide **what actions to take** and in **what order**.

```
User Query → [LLM Reasons] → [Takes Action] → [Observes Result] → [Reasons Again] → ... → Final Answer
```

### The key difference from a simple LLM call:
- **LLM call:** Input → Output (one shot)
- **Chain:** Input → Step 1 → Step 2 → ... → Output (fixed sequence)
- **Agent:** Input → [LLM decides next step dynamically] → ... → Output (flexible loop)

---

## The ReAct Pattern

**Re**asoning + **Act**ing — the most common agent architecture.

```
Loop:
  1. THOUGHT  — The LLM reasons about what to do next
  2. ACTION   — The LLM calls a tool with specific inputs
  3. OBSERVE  — The tool returns a result
  4. Repeat until the LLM has enough info to answer
```

### Example trace:

```
User: What is the population of France multiplied by 2?

Thought: I need to find the population of France. Let me search for it.
Action: search_web("population of France 2025")
Observation: France has a population of approximately 68.4 million.

Thought: Now I need to multiply 68.4 million by 2.
Action: calculate("68400000 * 2")
Observation: 136800000

Thought: I have the answer.
Final Answer: The population of France (approximately 68.4 million) multiplied by 2 is 136.8 million.
```

---

## Tool Calling

Modern LLMs don't just generate text — they can generate **structured tool calls**.

### How it works:
1. You describe available tools (name, description, parameters) to the LLM
2. The LLM decides if/when to use a tool
3. The LLM outputs a structured JSON call (not free text)
4. Your code executes the tool and feeds the result back

### Tool definition pattern:
```python
@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    return tavily_client.search(query)
```

The docstring matters — it's what the LLM reads to decide when to use the tool.

---

## When to Use What

| Approach | Use When |
|----------|----------|
| **Direct LLM call** | Simple Q&A, text generation, classification |
| **RAG** | Need factual answers grounded in your documents |
| **Agent** | Multi-step reasoning, dynamic tool use, tasks that need real-time data |
| **Multi-agent** | Complex workflows with distinct roles or parallel subtasks |

### Signs you need an agent:
- The task requires multiple steps that depend on intermediate results
- You need to call external APIs or tools dynamically
- The sequence of steps isn't known in advance

### Signs you DON'T need an agent:
- A simple prompt gets the job done
- The steps are always the same (use a chain instead)
- You need deterministic, reproducible output

---

## LangChain Overview

LangChain provides the building blocks:

- **Chat Models** — Unified interface to OpenAI, Anthropic, Google, etc.
- **Tools** — `@tool` decorator to turn any function into an agent tool
- **Agents** — `create_react_agent` wires an LLM to tools in a ReAct loop
- **Output Parsers** — Structure LLM outputs into Python objects

### Architecture:

```
                    ┌─────────────┐
User Query ───────▶│  ReAct Agent │
                    │  (LLM Loop) │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         ┌────────┐  ┌─────────┐  ┌──────────┐
         │ Search │  │  Calc   │  │ Wikipedia│
         └────────┘  └─────────┘  └──────────┘
```

---

## LangGraph Preview

LangGraph takes it further with **stateful, graph-based workflows**.

- LangChain agent = single loop with tools
- LangGraph = multiple nodes connected by edges, with shared state

### Why LangGraph?
- Explicit control flow (not just "LLM decides everything")
- Persistent state across steps
- Conditional branching and loops
- Human-in-the-loop approvals
- Checkpointing and recovery

We'll build a LangGraph workflow in Hands-on 2.

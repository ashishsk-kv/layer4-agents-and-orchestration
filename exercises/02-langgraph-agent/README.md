# Exercise 2: LangGraph Agent — Blog Writer Workflow

Build a stateful, multi-step workflow using LangGraph that plans, researches, writes, and reviews a blog post — with conditional routing and human-in-the-loop approval.

**Time:** ~70 minutes (across Day 1 + Day 2)
**File:** `starter.py` (fill in the TODOs) | `solution.py` (reference)

---

## What You'll Build

A Blog Writer workflow with four stages:

```
START → Planner → Researcher → Writer → Reviewer
                                  ↑         │
                                  └─────────┘ (needs revision)
                                        │
                                        ↓ (approved)
                                  Human Approval → END
```

- **Planner** — generates a structured outline from a topic
- **Researcher** — searches the web for supporting information
- **Writer** — drafts the article using the plan and research
- **Reviewer** — evaluates quality, sends back for revision or approves
- **Human approval** — pauses for human confirmation before final output

---

## Setup

```bash
git checkout 02-langgraph-agent
cd exercises/02-langgraph-agent
source ../../.venv/bin/activate
```

---

## Key Concepts

### StateGraph
A graph where nodes are functions and edges define the flow. All nodes share a typed state object.

### Nodes
Functions that receive the current state and return a partial update (only the fields they change).

### Edges
- **Regular:** `add_edge("A", "B")` — always go from A to B
- **Conditional:** `add_conditional_edges("A", route_fn, {...})` — route based on logic

### Reducers
Control how state updates merge. `Annotated[list, operator.add]` means list fields are appended, not overwritten.

### Checkpointing
Saves state at each step. Required for human-in-the-loop and for resuming workflows.

---

## Step-by-Step Instructions

### Step 1: Define the State

Open `starter.py` and define the `BlogWriterState` TypedDict with these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `topic` | `str` | The blog topic from the user |
| `plan` | `str` | The structured outline |
| `research` | `str` | Web research results |
| `draft` | `str` | The current draft |
| `feedback` | `str` | Reviewer feedback |
| `final_article` | `str` | The approved article |
| `revision_count` | `int` | Tracks how many revisions (max 2) |

---

### Step 2: Build the Planner Node

Create a function `plan_node(state)` that:
1. Takes the `topic` from state
2. Sends it to the LLM with a prompt asking for a structured blog outline
3. Returns `{"plan": outline_text}`

---

### Step 3: Build the Researcher Node

Create a function `research_node(state)` that:
1. Takes the `plan` from state
2. Uses Tavily search to find relevant information for each section
3. Returns `{"research": compiled_research}`

---

### Step 4: Build the Writer Node

Create a function `write_node(state)` that:
1. Takes `topic`, `plan`, `research`, and optionally `feedback` from state
2. Sends everything to the LLM with a writing prompt
3. If there's feedback, includes it so the LLM can address it
4. Returns `{"draft": article_text, "revision_count": state["revision_count"] + 1}`

---

### Step 5: Build the Reviewer Node + Conditional Routing

Create a function `review_node(state)` that:
1. Takes the `draft` from state
2. Asks the LLM to evaluate the draft for quality, accuracy, and completeness
3. The LLM must respond with either `APPROVED` or `NEEDS_REVISION: <feedback>`
4. Returns `{"feedback": feedback_text}` or `{"final_article": draft}` if approved

Create a routing function `should_revise(state)` that:
- Returns `"writer"` if feedback exists AND `revision_count < 2`
- Returns `"human_approval"` otherwise (either approved or max revisions hit)

---

### Step 6: Add Checkpointing and Human-in-the-Loop

1. Create a `human_approval_node` that uses `interrupt()` to pause for approval
2. Compile the graph with `MemorySaver` checkpointer
3. Invoke with a `thread_id` in the config
4. Resume with `Command(resume=...)` after human input

---

### Step 7: Visualize the Graph

Use `graph.get_graph().draw_mermaid_png()` to generate a visual diagram.
Alternatively, print the Mermaid text with `graph.get_graph().draw_mermaid()`.

---

## Running the Exercise

```bash
# Run the starter (will error at TODOs until you complete them)
python starter.py

# Run the solution
python solution.py
```

---

## Key Takeaways

1. **StateGraph** gives you explicit control flow, unlike an agent's free-form reasoning
2. **Conditional edges** let you build loops (review → revise → review again)
3. **Checkpointing** enables pause/resume and multi-turn workflows
4. **Human-in-the-loop** is built-in — just `interrupt()` and resume with `Command`
5. **State reducers** prevent accidental overwrites of accumulated data

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `interrupt()` not pausing | Make sure you compiled with a checkpointer and passed `thread_id` in config |
| State fields being overwritten | Use `Annotated[list, operator.add]` for fields that accumulate |
| Graph won't compile | Check that all nodes have at least one incoming and one outgoing edge |
| `draw_mermaid_png()` fails | This needs `pyppeteer` or an internet connection; use `draw_mermaid()` for text output instead |

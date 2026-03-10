# Exercise 1: LangChain Agent — Research Assistant

Build a ReAct agent that uses tools to answer complex questions requiring web search, calculation, and Wikipedia lookups.

**Time:** ~45 minutes
**File:** `starter.py` (fill in the TODOs) | `solution.py` (reference)

---

## What You'll Build

A Research Assistant agent that can:
- Search the web for current information (Tavily)
- Perform mathematical calculations
- Look up facts on Wikipedia
- Chain multiple tools together to answer complex queries

---

## Setup

Make sure you're in the right branch and your environment is active:

```bash
git checkout 01-langchain-agent
cd exercises/01-langchain-agent
source ../../.venv/bin/activate   # if not already active
```

Verify your `.env` file is in the repo root (`../../.env`) with your API keys set.

---

## Step-by-Step Instructions

### Step 1: Environment & LLM Setup

Open `starter.py` and complete the first TODO section.

- Load environment variables from `.env` using `dotenv`
- Initialize `ChatOpenAI` with model `gpt-4o` and temperature `0`

**Hint:** `load_dotenv()` looks for `.env` in the current directory by default. Use the `dotenv_path` parameter to point it to the repo root.

---

### Step 2: Define Tools

Create three tools using the `@tool` decorator:

#### 2a. Web Search Tool
- Use `TavilySearch` to search the web
- Wrap it so the agent gets clean string results

#### 2b. Calculator Tool
- Takes a math expression as a string
- Returns the evaluated result
- Handle errors gracefully

#### 2c. Wikipedia Tool
- Use `WikipediaQueryRun` with `WikipediaAPIWrapper`
- Searches Wikipedia and returns a summary

**Key concept:** The `@tool` decorator turns a Python function into something an LLM can call. The function's **docstring** is what the LLM reads to decide when to use it, so write clear, descriptive docstrings.

---

### Step 3: Create the Agent

- Collect your tools into a list
- Use `create_agent` from `langchain.agents` to create the agent
- Pass a `system_prompt` that defines the agent's personality and behavior

---

### Step 4: Test the Agent

Run your agent with these test queries:

```python
# Simple tool use
"What is the current population of Japan?"

# Multi-step reasoning
"What is the population of Germany? Multiply it by 3 and tell me the result."

# Wikipedia lookup
"Give me a brief summary of the Theory of Relativity from Wikipedia."
```

Run: `python starter.py`

You should see the agent reasoning through each step, calling tools, and synthesizing a final answer.

---

### Step 5: Add a Custom Tool

Write your own tool. Ideas:
- `get_current_time` — returns the current date and time
- `reverse_string` — reverses a given string
- `count_words` — counts words in a text

Add it to the tools list and test it with a relevant query.

---

### Step 6: Observe the ReAct Loop

Modify the agent invocation to stream events so you can see each step:

```python
for event in agent.stream({"messages": [("user", query)]}, stream_mode="values"):
    if event.get("messages"):
        last = event["messages"][-1]
        print(f"[{last.type}] {last.content[:200]}")
```

This reveals the Thought → Action → Observation loop in real time.

---

## Key Takeaways

1. **Tools are just functions** — the `@tool` decorator + a good docstring is all the LLM needs
2. **The agent decides** — you provide tools, the LLM decides when and how to use them
3. **ReAct loop** — the agent reasons, acts, observes, and repeats until it has an answer
4. **`create_agent`** — the simplest way to wire an LLM to tools in LangChain

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not set` | Check your `.env` file path in `load_dotenv()` |
| `TavilySearch` error | Verify `TAVILY_API_KEY` in `.env` |
| Agent loops forever | Add `max_iterations` or check your tool docstrings for clarity |
| Import errors | Run `pip install -r ../../requirements.txt` |

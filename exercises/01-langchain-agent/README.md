# Exercise 1: LangChain Chains & Agents

Build a deterministic LCEL chain **and** a ReAct agent with tools.

**Time:** ~45 minutes
**File:** `starter.py` (fill in the TODOs) | `solution.py` (reference)

---

## What You'll Build

**Part A — Chain:** A multi-step pipeline that searches the web, summarizes the research with one LLM call, and turns it into a tweet with a second LLM call.

**Part B — Agent:** A Research Assistant agent that can search the web, perform calculations, and look up Wikipedia — deciding *on its own* which tools to use and when.

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

## Part A: Build a LangChain Chain

### Step 1: Environment & LLM Setup

Open `starter.py` and complete the first TODO section.

- Load environment variables from `.env` using `dotenv`
- Initialize `ChatOpenAI` with model `gpt-4o` and temperature `0`

**Hint:** `load_dotenv()` looks for `.env` in the current directory by default. Use the `dotenv_path` parameter to point it to the repo root.

---

### Step 2: Simple Chain — prompt | llm | parser

Create a basic LCEL chain that explains a topic:

1. Create a `ChatPromptTemplate` with a system message and a `{topic}` placeholder
2. Create a `StrOutputParser`
3. Chain them together with `|`: `prompt | llm | parser`
4. Call `.invoke({"topic": "quantum computing"})` to test

**Key concept:** The `|` pipe operator creates a `Runnable` pipeline. Each step receives the output of the previous step. Every chain has `.invoke()`, `.stream()`, and `.batch()`.

---

### Step 3: Multi-step Chain — search → LLM #1 → LLM #2

Build a pipeline that chains **multiple LLM calls** with a tool call in between:

1. **Search step** — use `TavilySearch` to search the web for a topic
2. **LLM call #1** — summarize the research into 3 bullet points
3. **LLM call #2** — turn the summary into a catchy tweet

Use `RunnableLambda` to wrap Python functions (like the search step) as chainable steps. Use separate `ChatPromptTemplate` for each LLM call.

```
Topic → [Tavily Search] → [LLM #1: Summarize] → [LLM #2: Tweet] → Output
```

**Key concept:** This is still a **chain** — the steps always run in the same fixed order. The LLM has no choice about what happens next. If you can draw it as a straight line, it's a chain.

Run `python starter.py` — you should see output from both chains before the agent section.

---

## Part B: Build a LangChain Agent

### Step 4: Define Tools

Create three tools using the `@tool` decorator:

#### 4a. Web Search Tool
- Use `TavilySearch` to search the web
- Wrap it so the agent gets clean string results

#### 4b. Calculator Tool
- Takes a math expression as a string
- Returns the evaluated result
- Handle errors gracefully

#### 4c. Wikipedia Tool
- Use `WikipediaQueryRun` with `WikipediaAPIWrapper`
- Searches Wikipedia and returns a summary

**Key concept:** The `@tool` decorator turns a Python function into something an LLM can call. The function's **docstring** is what the LLM reads to decide when to use it, so write clear, descriptive docstrings.

---

### Step 5: Create the Agent

- Collect your tools into a list
- Use `create_agent` from `langchain.agents` to create the agent
- Pass a `system_prompt` that defines the agent's personality and behavior

---

### Step 6: Test the Agent

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

### Step 7: Add a Custom Tool (Bonus)

Write your own tool. Ideas:
- `get_current_time` — returns the current date and time
- `reverse_string` — reverses a given string
- `count_words` — counts words in a text

Add it to the tools list and test it with a relevant query.

---

### Step 8: Observe the ReAct Loop

Uncomment the streaming section at the bottom of the file to see each step:

```python
for event in agent.stream({"messages": [("user", query)]}, stream_mode="values"):
    if event.get("messages"):
        last = event["messages"][-1]
        print(f"[{last.type}] {last.content[:200]}")
```

This reveals the Thought → Action → Observation loop in real time.

---

## Key Takeaways

1. **Chains are fixed pipelines** — `prompt | llm | parser` always follows the same path, even with multiple LLM calls
2. **Agents are reasoning loops** — the LLM decides which tools to call and when to stop
3. **`RunnableLambda`** — wraps any Python function into a chainable step
4. **Tools are just functions** — the `@tool` decorator + a good docstring is all the LLM needs
5. **`create_agent`** — the simplest way to wire an LLM to tools in LangChain

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not set` | Check your `.env` file path in `load_dotenv()` |
| `TavilySearch` error | Verify `TAVILY_API_KEY` in `.env` |
| Agent loops forever | Add `max_iterations` or check your tool docstrings for clarity |
| Import errors | Run `pip install -r ../../requirements.txt` |

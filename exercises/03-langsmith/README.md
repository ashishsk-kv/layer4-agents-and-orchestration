# Exercise 3: LangSmith — Tracing, Evaluation & Prompt Management

Add production-grade observability to your AI agents with LangSmith. Learn to trace executions, build evaluation datasets, run LLM-as-judge evaluators, and manage prompts.

**Time:** ~45 minutes
**Files:**
- `starter_tracing.py` / `solution_tracing.py` — Tracing & custom spans
- `starter_eval.py` / `solution_eval.py` — Evaluation & prompt management

---

## What You'll Build

1. **Automatic tracing** — See every LLM call, tool invocation, and decision in the LangSmith UI
2. **Custom traces** — Add your own spans with `@traceable` for business logic
3. **Evaluation dataset** — A golden set of question-answer pairs
4. **LLM-as-judge evaluator** — Automated quality scoring with a judge LLM
5. **Prompt management** — Push, pull, and version prompts in LangSmith

---

## Setup

```bash
git checkout 03-langsmith
cd exercises/03-langsmith
source ../../.venv/bin/activate
```

Make sure your `.env` has all three keys set:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
LANGSMITH_API_KEY=lsv2-...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=layer4-workshop
```

Open the LangSmith UI at https://smith.langchain.com — you'll be checking traces here throughout the exercise.

---

## Part A: Tracing (~20 min)

Work in `starter_tracing.py`.

### Step 1: Enable Automatic Tracing

Just loading the env vars enables tracing for all LangChain/LangGraph code. Complete the TODO to:
1. Load the `.env` file
2. Create a simple LangChain chain (prompt | LLM | parser)
3. Invoke it and check the LangSmith UI for the trace

After running, go to https://smith.langchain.com, select the `layer4-workshop` project, and find your trace. Click into it to see the prompt, response, tokens, and latency.

### Step 2: Custom Traces with `@traceable`

The `@traceable` decorator wraps any function as a traced span:
- Nested `@traceable` functions create child spans automatically
- You can tag traces with metadata for filtering

Complete the TODO to:
1. Create a `@traceable` research pipeline with nested functions
2. Add metadata tags for filtering in the UI
3. Run it and find the nested spans in LangSmith

### Step 3: Trace a ReAct Agent

Build a simple agent (like Exercise 1) and observe how LangSmith automatically traces:
- Each iteration of the ReAct loop
- Every tool call and its result
- The LLM's reasoning at each step
- Total tokens and latency

---

## Part B: Evaluation & Prompt Management (~25 min)

Work in `starter_eval.py`.

### Step 4: Create an Evaluation Dataset

Build a dataset of question-answer pairs that represent "golden" examples — these are the ground truth your agent should match.

Complete the TODO to:
1. Initialize the LangSmith `Client`
2. Create a dataset with `client.create_dataset()`
3. Add 5+ examples with `client.create_examples()`

### Step 5: Build an LLM-as-Judge Evaluator

Traditional `assert output == expected` doesn't work for LLM outputs. Instead, use another LLM to judge quality.

Complete the TODO to:
1. Create a correctness evaluator using `openevals`
2. Define a target function (the agent/chain you want to evaluate)
3. Run `client.evaluate()` on your dataset
4. View results in the LangSmith UI under "Experiments"

### Step 6: Prompt Management

LangSmith can store and version your prompts:

Complete the TODO to:
1. Push a prompt to LangSmith with `client.push_prompt()`
2. Pull it back with `client.pull_prompt()`
3. Use the pulled prompt in a chain
4. Update the prompt and push a new version
5. Compare the two versions in the LangSmith UI

---

## Key Takeaways

1. **Tracing is free (almost)** — Just set env vars and every LangChain call is traced
2. **`@traceable` is your friend** — Wrap any function to see it in the trace tree
3. **Eval datasets are essential** — Without them, you're guessing about quality
4. **LLM-as-judge scales** — You can evaluate hundreds of outputs automatically
5. **Prompt management** — Treat prompts like code: version, test, deploy

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No traces in UI | Check `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in your `.env` |
| Wrong project | Check `LANGSMITH_PROJECT` matches what you see in the UI |
| `openevals` import error | Run `pip install openevals` |
| Dataset already exists | Use a unique name or delete the old one in the UI |
| Rate limits | LangSmith free tier allows 5000 traces/month — plenty for a workshop |

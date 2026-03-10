# Day 2: LangSmith — Observability for AI

## Why Observability Matters

Traditional software: you can read the code path to understand behavior.
AI systems: the "logic" lives inside an LLM that reasons non-deterministically.

### Without observability:
- You can't see *why* the agent chose a particular tool
- You can't measure if prompt changes improved quality
- Debugging is "add print statements and hope"
- You don't know how much each call costs

### With LangSmith:
- Full trace of every LLM call, tool invocation, and decision
- Latency and token usage breakdowns
- Evaluation frameworks to measure quality systematically
- Prompt versioning and management

---

## What LangSmith Provides

```
┌──────────────────────────────────────────┐
│               LangSmith                  │
│                                          │
│  ┌──────────┐  ┌────────────┐  ┌──────┐ │
│  │ Tracing  │  │ Evaluation │  │Prompt│ │
│  │          │  │            │  │  Hub │ │
│  │ - Runs   │  │ - Datasets │  │      │ │
│  │ - Spans  │  │ - Judges   │  │- Push│ │
│  │ - Costs  │  │ - Metrics  │  │- Pull│ │
│  │ - Tokens │  │ - Compare  │  │- Tag │ │
│  └──────────┘  └────────────┘  └──────┘ │
└──────────────────────────────────────────┘
```

---

## Tracing: How It Works

1. Set environment variables:
   ```
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=<key>
   ```

2. Run your LangChain/LangGraph code normally — traces are sent automatically.

3. View in the LangSmith UI:
   - Each "run" shows the full execution tree
   - Every LLM call shows: prompt, response, tokens, latency
   - Tool calls show: input, output, duration

### Custom tracing with `@traceable`:
```python
@traceable
def my_pipeline(question: str) -> str:
    # Everything inside is traced as a single span
    ...
```

---

## Evaluation: Measuring Quality

Traditional tests: `assert output == expected` (exact match).
LLM evaluation: outputs vary, so we need **judgment-based evaluation**.

### LLM-as-Judge:
- Use a separate LLM to score your agent's outputs
- Define criteria: correctness, helpfulness, relevance
- Run on a dataset of examples
- Compare experiments over time

### Workflow:
```
Dataset (inputs + expected outputs)
        │
        ▼
  Target Function (your agent)
        │
        ▼
   Evaluators (LLM-as-judge, code checks)
        │
        ▼
  Experiment Results (scores, comparisons)
```

---

## Prompt Management

LangSmith also serves as a **prompt registry**:

- **Push** prompts with version tags (`dev`, `staging`, `prod`)
- **Pull** prompts in your code — swap prompts without deploying
- **Test** prompts in the Playground before going live
- **Compare** prompt versions side-by-side with evaluation results

This is essential for production AI systems where prompt changes are the primary way you "update the code."

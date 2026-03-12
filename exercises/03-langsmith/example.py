"""
DEMO: LangSmith Building Blocks
=================================
Run this BEFORE starting the exercise. It shows automatic tracing,
custom spans, and a quick evaluation — then you check the results
live in the LangSmith UI.

Run with: python example.py
Then open: https://smith.langchain.com → project "layer4-workshop"
"""

import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langsmith import Client, traceable

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

llm = ChatOpenAI(model="gpt-4o", temperature=0)


# ─────────────────────────────────────────────────────────────
def demo_1_auto_tracing():
    """Any LangChain call is traced automatically — zero extra code."""
    print("=" * 60)
    print("DEMO 1: Automatic Tracing (chain)")
    print("=" * 60)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer in one sentence."),
        ("user", "{question}"),
    ])
    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({"question": "What is LangSmith?"})
    print(f"Answer: {result}")
    print()
    print("→ Open LangSmith UI. You should see a trace with:")
    print("  ChatPromptTemplate → ChatOpenAI → StrOutputParser")
    print()


# ─────────────────────────────────────────────────────────────
def demo_2_traceable_decorator():
    """@traceable wraps any function as a span in the trace tree."""
    print("=" * 60)
    print("DEMO 2: Custom Traces with @traceable")
    print("=" * 60)

    @traceable
    def fetch_joke(topic: str) -> str:
        """This entire function becomes one span in LangSmith."""
        response = llm.invoke([
            ("system", "Tell a short one-liner joke."),
            ("user", f"Topic: {topic}"),
        ])
        return response.content

    @traceable(metadata={"demo": "nested-spans"})
    def joke_pipeline(topic: str) -> dict:
        """Parent span — fetch_joke becomes a child span inside it."""
        joke = fetch_joke(topic)
        rating = llm.invoke([
            ("system", "Rate this joke from 1-10. Reply with just the number."),
            ("user", joke),
        ])
        return {"joke": joke, "rating": rating.content.strip()}

    result = joke_pipeline("software engineers")
    print(f"Joke:   {result['joke']}")
    print(f"Rating: {result['rating']}/10")
    print()
    print("→ In LangSmith you should see a nested trace:")
    print("  joke_pipeline")
    print("    ├── fetch_joke")
    print("    │     └── ChatOpenAI")
    print("    └── ChatOpenAI (rating)")
    print()


# ─────────────────────────────────────────────────────────────
def demo_3_agent_tracing():
    """Agent traces show every step of the ReAct loop automatically."""
    print("=" * 60)
    print("DEMO 3: Agent Tracing (ReAct loop)")
    print("=" * 60)

    tavily = TavilySearch(max_results=2)

    @tool
    def search_web(query: str) -> str:
        """Search the web for current information."""
        response = tavily.invoke(query)
        return "\n".join(
            f"- {r['content'][:150]}" for r in response["results"]
        )

    @tool
    def calculate(expression: str) -> str:
        """Evaluate a math expression like '2 + 2'."""
        try:
            return str(eval(expression, {"__builtins__": {}}, {}))
        except Exception as e:
            return f"Error: {e}"

    agent = create_agent(
        llm,
        [search_web, calculate],
        system_prompt="You are a helpful assistant. Use tools when needed.",
    )

    result = agent.invoke({
        "messages": [("user", "What is 42 * 58? Also search for who invented Python.")]
    })
    print(f"Answer: {result['messages'][-1].content[:300]}")
    print()
    print("→ In LangSmith you should see the full ReAct loop:")
    print("  Agent → LLM (reason) → Tool (act) → LLM (reason) → ...")
    print()


# ─────────────────────────────────────────────────────────────
def demo_4_quick_eval():
    """Create a tiny dataset and run a one-shot evaluation."""
    print("=" * 60)
    print("DEMO 4: Quick Evaluation")
    print("=" * 60)

    client = Client()

    dataset_name = f"demo-eval-{uuid.uuid4().hex[:6]}"
    dataset = client.create_dataset(
        dataset_name,
        description="Quick demo dataset",
    )

    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"question": "What is the capital of Japan?"},
                "outputs": {"answer": "Tokyo"},
            },
            {
                "inputs": {"question": "What is 7 * 8?"},
                "outputs": {"answer": "56"},
            },
            {
                "inputs": {"question": "Who wrote Romeo and Juliet?"},
                "outputs": {"answer": "William Shakespeare"},
            },
        ],
    )
    print(f"Created dataset: {dataset_name} (3 examples)")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer concisely in one sentence."),
        ("user", "{question}"),
    ])
    chain = prompt | llm | StrOutputParser()

    def target(inputs: dict) -> dict:
        return {"answer": chain.invoke({"question": inputs["question"]})}

    def simple_judge(inputs, outputs, reference_outputs):
        judge_response = llm.invoke([
            (
                "system",
                "You are a grading assistant. Compare the actual answer to the "
                "expected answer. Reply with ONLY 'correct' or 'incorrect'.",
            ),
            (
                "user",
                f"Question: {inputs['question']}\n"
                f"Expected: {reference_outputs['answer']}\n"
                f"Actual: {outputs['answer']}",
            ),
        ])
        is_correct = "correct" in judge_response.content.lower().split()[0]
        return {"key": "correctness", "score": 1.0 if is_correct else 0.0}

    results = client.evaluate(
        target,
        data=dataset_name,
        evaluators=[simple_judge],
        experiment_prefix="demo-eval",
        max_concurrency=2,
    )
    print(f"Evaluation complete!")
    print(f"Experiment name: {results.experiment_name}")
    print(f"View at: https://smith.langchain.com → Datasets → Experiments")
    print()
    print("→ In LangSmith → Datasets → Experiments, you'll see scores for each example.")
    print()


if __name__ == "__main__":
    print()
    print("Layer 4 Workshop — LangSmith Demo")
    print("This demo walks through tracing, @traceable, and evaluation.")
    print("Keep https://smith.langchain.com open to see results in real time.")
    print()

    demo_1_auto_tracing()
    demo_2_traceable_decorator()
    demo_3_agent_tracing()
    demo_4_quick_eval()

    print("=" * 60)
    print("That's it! Now open starter_tracing.py and starter_eval.py")
    print("to build your own tracing pipeline and evaluation suite.")
    print("=" * 60)

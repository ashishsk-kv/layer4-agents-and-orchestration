"""
Exercise 3 — Part B: LangSmith Evaluation & Prompt Management (SOLUTION)
=========================================================================
Evaluation datasets, LLM-as-judge evaluators, and prompt management.

Run with: python solution_eval.py
Then check results at https://smith.langchain.com
"""

import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import Client
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

# ============================================================
# Environment Setup
# ============================================================

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Client()


# ============================================================
# STEP 4: Create an Evaluation Dataset
# ============================================================

def step4_create_dataset() -> str:
    print("\n--- Step 4: Create Evaluation Dataset ---")

    dataset_name = f"layer4-workshop-qa-{uuid.uuid4().hex[:6]}"

    dataset = client.create_dataset(
        dataset_name,
        description="QA pairs for evaluating our research assistant",
    )

    client.create_examples(
        dataset_id=dataset.id,
        examples=[
            {
                "inputs": {"question": "What is the capital of France?"},
                "outputs": {"answer": "The capital of France is Paris."},
            },
            {
                "inputs": {"question": "What programming language is LangChain written in?"},
                "outputs": {"answer": "LangChain is primarily written in Python, with a JavaScript/TypeScript version as well."},
            },
            {
                "inputs": {"question": "What does RAG stand for in AI?"},
                "outputs": {"answer": "RAG stands for Retrieval-Augmented Generation."},
            },
            {
                "inputs": {"question": "What is the purpose of an embedding model?"},
                "outputs": {"answer": "An embedding model converts text into dense numerical vectors that capture semantic meaning, enabling similarity search and retrieval."},
            },
            {
                "inputs": {"question": "Name one advantage of using agents over simple LLM calls."},
                "outputs": {"answer": "Agents can dynamically decide which tools to use and in what order, enabling multi-step reasoning and interaction with external systems."},
            },
            {
                "inputs": {"question": "What is the ReAct pattern?"},
                "outputs": {"answer": "ReAct combines Reasoning and Acting — the LLM alternates between thinking about what to do and taking actions (tool calls) in a loop until it reaches a final answer."},
            },
        ],
    )

    print(f"Created dataset: {dataset_name} with 6 examples")
    print(f"View at: https://smith.langchain.com → Datasets")
    return dataset_name


# ============================================================
# STEP 5: Build an LLM-as-Judge Evaluator
# ============================================================

def step5_run_evaluation(dataset_name: str):
    print("\n--- Step 5: LLM-as-Judge Evaluation ---")

    if dataset_name is None:
        print("ERROR: No dataset name. Complete Step 4 first.")
        return

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the following question accurately and concisely."),
        ("user", "{question}"),
    ])
    chain = prompt | llm | StrOutputParser()

    def answer_question(inputs: dict) -> dict:
        """The target function being evaluated."""
        answer = chain.invoke({"question": inputs["question"]})
        return {"answer": answer}

    def correctness_evaluator(inputs, outputs, reference_outputs):
        evaluator = create_llm_as_judge(
            prompt=CORRECTNESS_PROMPT,
            model="openai:gpt-4o",
            feedback_key="correctness",
        )
        return evaluator(
            inputs=inputs,
            outputs=outputs,
            reference_outputs=reference_outputs,
        )

    results = client.evaluate(
        answer_question,
        data=dataset_name,
        evaluators=[correctness_evaluator],
        experiment_prefix="workshop-eval",
        max_concurrency=2,
    )

    print(f"Evaluation complete!")
    print(f"Experiment: {results.experiment_name}")
    print(f"View at: https://smith.langchain.com → Datasets → Experiments")


# ============================================================
# STEP 6: Prompt Management
# ============================================================

def step6_prompt_management():
    print("\n--- Step 6: Prompt Management ---")

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    parser = StrOutputParser()

    # Version 1: Basic prompt
    prompt_v1 = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that specializes in {domain}."),
        ("user", "{question}"),
    ])

    prompt_name = f"workshop-qa-prompt-{uuid.uuid4().hex[:6]}"

    url = client.push_prompt(prompt_name, object=prompt_v1)
    print(f"Pushed prompt v1: {url}")

    # Pull it back and use it
    pulled_prompt = client.pull_prompt(prompt_name)
    chain_v1 = pulled_prompt | llm | parser
    result_v1 = chain_v1.invoke({
        "domain": "science",
        "question": "What is DNA?",
    })
    print(f"v1 response: {result_v1[:150]}")

    # Version 2: Enhanced prompt
    prompt_v2 = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert in {domain}. Give detailed, accurate answers "
            "with concrete examples. Structure your response with bullet points "
            "when listing multiple items.",
        ),
        ("user", "{question}"),
    ])

    client.push_prompt(prompt_name, object=prompt_v2)
    print(f"Pushed prompt v2 (same name, new version)")

    # Use v2
    pulled_v2 = client.pull_prompt(prompt_name)
    chain_v2 = pulled_v2 | llm | parser
    result_v2 = chain_v2.invoke({
        "domain": "science",
        "question": "What is DNA?",
    })
    print(f"v2 response: {result_v2[:150]}")

    print(f"\nCompare both versions in LangSmith → Prompts → {prompt_name}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 3, Part B: Evaluation & Prompts (SOLUTION)")
    print("=" * 60)
    print("View results at: https://smith.langchain.com")
    print("=" * 60)

    dataset_name = step4_create_dataset()
    step5_run_evaluation(dataset_name)
    step6_prompt_management()

    print("\n" + "=" * 60)
    print("Done! Check LangSmith for:")
    print("  - Datasets: your QA evaluation dataset")
    print("  - Experiments: your evaluation run results")
    print("  - Prompts: your versioned prompts")
    print("=" * 60)

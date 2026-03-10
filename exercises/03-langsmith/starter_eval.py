"""
Exercise 3 — Part B: LangSmith Evaluation & Prompt Management
===============================================================
Build evaluation datasets, run LLM-as-judge evaluators, and
manage prompts with LangSmith.

Instructions: Fill in each TODO section. Run with: python starter_eval.py
Then check results at https://smith.langchain.com
"""

import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langsmith import Client

# ============================================================
# Environment Setup
# ============================================================

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# ============================================================
# STEP 4: Create an Evaluation Dataset
# ============================================================

# TODO: Create a dataset of question-answer pairs in LangSmith.
#
# 1. Initialize the LangSmith client: client = Client()
# 2. Create a dataset:
#    dataset = client.create_dataset(
#        "layer4-workshop-qa",
#        description="QA pairs for evaluating our research assistant"
#    )
# 3. Add examples with client.create_examples():
#    client.create_examples(
#        dataset_id=dataset.id,
#        examples=[
#            {
#                "inputs": {"question": "What is the capital of France?"},
#                "outputs": {"answer": "The capital of France is Paris."},
#            },
#            ... (add at least 5 examples)
#        ],
#    )
#
# After running, go to LangSmith → Datasets to see your dataset.

def step4_create_dataset():
    print("\n--- Step 4: Create Evaluation Dataset ---")

    # Your code here:
    pass

    # Return the dataset name so Step 5 can use it
    return None  # <-- Return the dataset name string


# ============================================================
# STEP 5: Build an LLM-as-Judge Evaluator
# ============================================================

# TODO: Create an evaluator and run it against your dataset.
#
# 1. Define your target function (the thing being evaluated):
#    def answer_question(inputs: dict) -> dict:
#        """Simple QA chain — this is what we're evaluating."""
#        llm = ChatOpenAI(model="gpt-4o", temperature=0)
#        prompt = ChatPromptTemplate.from_messages([
#            ("system", "Answer the following question accurately and concisely."),
#            ("user", "{question}"),
#        ])
#        chain = prompt | llm | StrOutputParser()
#        answer = chain.invoke({"question": inputs["question"]})
#        return {"answer": answer}
#
# 2. Define a correctness evaluator using openevals:
#    from openevals.llm import create_llm_as_judge
#    from openevals.prompts import CORRECTNESS_PROMPT
#
#    def correctness_evaluator(inputs, outputs, reference_outputs):
#        evaluator = create_llm_as_judge(
#            prompt=CORRECTNESS_PROMPT,
#            model="openai:gpt-4o",
#            feedback_key="correctness",
#        )
#        return evaluator(
#            inputs=inputs,
#            outputs=outputs,
#            reference_outputs=reference_outputs,
#        )
#
# 3. Run the evaluation:
#    client = Client()
#    results = client.evaluate(
#        answer_question,
#        data="layer4-workshop-qa",  # your dataset name
#        evaluators=[correctness_evaluator],
#        experiment_prefix="workshop-eval",
#        max_concurrency=2,
#    )
#    print(f"Experiment: {results.experiment_name}")
#
# 4. View results in LangSmith → Experiments

def step5_run_evaluation(dataset_name: str):
    print("\n--- Step 5: LLM-as-Judge Evaluation ---")

    if dataset_name is None:
        print("ERROR: No dataset name. Complete Step 4 first.")
        return

    # Your code here:
    pass


# ============================================================
# STEP 6: Prompt Management
# ============================================================

# TODO: Push, pull, and version prompts in LangSmith.
#
# 1. Create a prompt:
#    prompt = ChatPromptTemplate.from_messages([
#        ("system", "You are a helpful assistant that specializes in {domain}."),
#        ("user", "{question}"),
#    ])
#
# 2. Push it to LangSmith:
#    client = Client()
#    prompt_name = "workshop-qa-prompt"
#    url = client.push_prompt(prompt_name, object=prompt)
#    print(f"Prompt pushed: {url}")
#
# 3. Pull it back and use it:
#    pulled_prompt = client.pull_prompt(prompt_name)
#    llm = ChatOpenAI(model="gpt-4o", temperature=0)
#    chain = pulled_prompt | llm | StrOutputParser()
#    result = chain.invoke({"domain": "science", "question": "What is DNA?"})
#
# 4. Update the prompt and push a new version:
#    updated_prompt = ChatPromptTemplate.from_messages([
#        ("system", "You are an expert in {domain}. Give detailed, accurate answers with examples."),
#        ("user", "{question}"),
#    ])
#    client.push_prompt(prompt_name, object=updated_prompt)
#
# 5. Go to LangSmith → Prompts to see both versions

def step6_prompt_management():
    print("\n--- Step 6: Prompt Management ---")

    # Your code here:
    pass


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("Layer 4 Workshop — Exercise 3, Part B: Evaluation & Prompts")
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

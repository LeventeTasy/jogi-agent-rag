import os
import time
from deepeval.models import GeminiModel, AzureOpenAIModel
from deepeval.test_case import LLMTestCase
from deepeval.test_case import LLMTestCaseParams
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    SummarizationMetric,
    ToxicityMetric,
    BiasMetric,
    GEval
)
from dotenv import load_dotenv
import os
import json
import pandas as pd
from pathlib import Path

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")


def evaluate_multi_agent_system(input_text, actual_output, retrieval_context):
    """
    MODEL_NAME = "gemini-flash-lite-latest"

    model = GeminiModel(
        model=MODEL_NAME,
        api_key=API_KEY,
        temperature=0
    )"""

    model = AzureOpenAIModel(
        model="gpt-5-mini",
        deployment_name="gpt-5-mini",
        api_key=API_KEY,
        api_version="2025-01-01-preview",
        base_url=BASE_URL,
        temperature=0.5
    )

    faithfulness = FaithfulnessMetric(threshold=0.5, model=model)
    answer_relevancy = AnswerRelevancyMetric(threshold=0.5, model=model)
    context_relevancy = ContextualRelevancyMetric(threshold=0.5, model=model)

    """
    coherence = GEval(
        name="Coherence",
        criteria="Determine how logically connected, flowy and coherent the actual output is.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.5,
        model=model
    )"""

    try:
        test_case = LLMTestCase(
            input=input_text,
            actual_output=actual_output,
            retrieval_context=retrieval_context
        )

        metrics = [
            faithfulness, answer_relevancy, context_relevancy
        ]

        metric_names = ["Faithfulness", "Answer_Relevancy", "Context_Relevancy"]

        for metric, metric_name in zip(metrics, metric_names):
            metric.measure(test_case)

            try:
                print(metric_name + ": " + str(metric.score))
                print(metric_name + ": " + str(metric.reason))
            except:
                print("Hiba a kiiratásnál!")

    except TypeError:
        test_case = LLMTestCase(
            input=input_text,
            actual_output=actual_output,
            retrieval_context=None
        )

        metrics = [
            answer_relevancy
        ]

        metric_names = ["Answer_Relevancy"]

        for metric, metric_name in zip(metrics, metric_names):
            metric.measure(test_case)

            try:
                print(metric_name + ": " + str(metric.score))
                print(metric_name + ": " + str(metric.reason))
            except:
                print("Hiba a kiiratásnál!")

    results = {
            "Faithfulness": faithfulness.score,
            "Faithfulness_Reason": faithfulness.reason,
            "Answer_Relevancy": answer_relevancy.score,
            "Answer_Relevancy_Reason": answer_relevancy.reason,
            "Context_Relevancy": context_relevancy.score,
            "Context_Relevancy_Reason": context_relevancy.reason,
    }

    return results

COLUMNS = [
    "Torveny", "Tipus", "Kerdes", "Q_chunk", "A_chunk",
    "Valasz", "Faithfulness", "Faithfulness_Reason", "Answer_Relevancy", "Answer_Relevancy_Reason", "Context_Relevancy","Context_Relevancy_Reason" ,
    "Summarization", "Summarization_Reason" , "Coherance", "Coherance_Reason","Toxicity", "Toxicity_Reason","Bias", "Bias_Reason" # osszesen: 20 oszlop
    # str, str, str, str, str, str, float, str, float, str, float, str, float, str, float, str, float, str, float, str
]

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    PATH = BASE_DIR.parent / "results" / "answered_questions_rag.xlsx"

    limit = 22
    ind = 0

    if os.path.exists(PATH):
        df = pd.read_excel(PATH, dtype=object)
        #print(df.dtypes)

        for index, row in df.iterrows():
            if ind >= limit:
                break

            jelenlegi_valasz = row['Valasz']
            jelenlegi_achunk = row['A_chunk']
            faithfulness_reason = row['Faithfulness_Reason']

            valasz_ures = pd.isna(jelenlegi_valasz) or str(jelenlegi_valasz).strip() == ""
            achunk_ures = pd.isna(jelenlegi_achunk) or str(jelenlegi_achunk).strip() == ""
            faithfulness_reason_ures = pd.isna(faithfulness_reason) or str(faithfulness_reason).strip() == ""

            if valasz_ures and achunk_ures:
                print(f"Sor [{index}] még nincs megválaszolva, kihagyás.")
                continue

            if not faithfulness_reason_ures:
                print(f"Sor [{index}] már ki van töltve, kihagyás.")
                continue

            input_q = row['Kerdes']
            agent_output = row['Valasz']
            retrieved_rag_chunks = [row["A_chunk"]]
            print("-" * 30)
            print(f"Kérdés feldolgozása: {input_q}")


            eredmenyek = evaluate_multi_agent_system(input_q,agent_output,retrieved_rag_chunks)

            for key in eredmenyek.keys():
                df.at[index, key] = eredmenyek[key]

            df.to_excel(PATH, index=False)
            #print(json.dumps(eredmenyek, indent=4, ensure_ascii=False))
            print("-" * 30)
            print("\n\n")


            ind+=1
    else:
        raise FileNotFoundError
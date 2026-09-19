import os, sys
from datetime import datetime

import pandas as pd
import time
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
chatID = f"T_{datetime.now().strftime("%Y-%m-%d %H:%M:%S").upper()}"

if project_root not in sys.path:
    sys.path.append(project_root)
from src.jogi_agent.flow import JogiFlow
from src.rag import ask_question

BASE_DIR = Path(__file__).resolve().parent
MODEL_IS_AGENT = True # True -> AGENT | False -> RAG
PATH = BASE_DIR.parent / "datasets" / "model_comparison" / "test_questions.csv"

if MODEL_IS_AGENT:
    SAVE_PATH = BASE_DIR.parent / "results" / "model_comparison" / "answered_questions_agent_unified_grounding.csv"
else:
    SAVE_PATH = BASE_DIR.parent / "results" / "answered_questions_rag.csv"


AGENT_COLUMNS = [
    "Torveny",
    "Tipus",
    "Kerdes",
    "Q_chunk",
    "A_chunk",
    "Valasz",
    "Faithfulness",
    "Faithfulness_Reason",
    "Answer_Relevancy",
    "Answer_Relevancy_Reason",
    "Context_Relevancy",
    "Context_Relevancy_Reason",
    "Verifier_Agent_Runs",
    "Runtime",
    "Question_ID",
    "Timestamp",
    "Total_Tokens", "Prompt_Tokens", "Completion_Tokens", "Successful_Requests"
] # str, str, str, str, str, str, float, str, float, str, float, str, int, float, str, str, int, int, int, int

RAG_COLUMNS = [
    "Torveny",
    "Tipus",
    "Kerdes",
    "Q_chunk",
    "A_chunk",
    "Valasz",
    "Faithfulness",
    "Faithfulness_Reason",
    "Answer_Relevancy",
    "Answer_Relevancy_Reason",
    "Context_Relevancy",
    "Context_Relevancy_Reason",
    "Runtime"
] # str, str, str, str, str, str, float, str, float, str, float, str, float,

if os.path.exists(SAVE_PATH):
    df = pd.read_csv(SAVE_PATH)
else:
    df = pd.read_csv(PATH)


text_columns = [
    "Valasz",
    "A_chunk",
    "Q_chunk",
    "Faithfulness_Reason",
    "Answer_Relevancy_Reason",
    "Question_ID",
    "Timestamp"
]

for col in text_columns:
    df[col] = df[col].astype("string")

print(f"{len(df)} tesztkérdés beolvasva!")

limit = 100
ind = 0

print(f"Running the {'Agent' if MODEL_IS_AGENT else 'RAG'} model...")

for index, row in df.iterrows():

    if ind >= limit:
        break

    jelenlegi_valasz = row['Valasz']
    jelenlegi_achunk = row['A_chunk']

    valasz_ures = pd.isna(jelenlegi_valasz) or str(jelenlegi_valasz).strip() == ""
    achunk_ures = pd.isna(jelenlegi_achunk) or str(jelenlegi_achunk).strip() == ""

    if not valasz_ures and not achunk_ures:
        print(f"Sor [{index}] már ki van töltve, kihagyás.")
        continue

    kerdes = row['Kerdes']
    print(f"Sor [{index}]: Feldolgozás alatt... Kérdés: '{kerdes[:50]}...'")

    inputs = {
            'topic': kerdes,
            'history': "",
            'details': "",
            'da_questions': "",
            'da_answers': "",
            'username': "T_1",
            "chatID": chatID,
            "questionNumber": index
        }

    if MODEL_IS_AGENT:
        start_time = time.perf_counter()
        flow = JogiFlow()
        flow.state["inputs"] = inputs

        answer = str(flow.kickoff())
        elapsed_time = time.perf_counter() - start_time

        print(answer+"\n\n")
        chunks_list = flow.get_chunks()
        a_chunk_string = "\n\n".join(chunks_list)

        verifier_retries = flow.get_verifier_counter()
        questionID = flow.get_question_id()
        metrics = flow.get_metrics()

        df.at[index, 'Total_Tokens'] = metrics["totalTokens"]
        df.at[index, 'Prompt_Tokens'] = metrics["promptTokens"]
        df.at[index, 'Completion_Tokens'] = metrics["completionTokens"]
        df.at[index, 'Successful_Requests'] = metrics["successfulRequests"]

        df.at[index, "Verifier_Agent_Runs"] = int(verifier_retries)
        df.at[index, "Question_ID"] = questionID


    else:
        start_time = time.perf_counter()
        answer, a_chunk_string = ask_question(kerdes)
        elapsed_time = time.perf_counter() - start_time
        #print(a_chunk_string)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    uj_valasz = f"Sikeresen generált válasz a(z) {index}. sorhoz!"

    df.at[index, 'Valasz'] = answer
    df.at[index, 'A_chunk'] = a_chunk_string
    df.at[index, 'Runtime'] = elapsed_time
    df.at[index, "Timestamp"] = timestamp

    df.to_csv(SAVE_PATH, index=False, encoding="utf-8-sig")

    ind+=1



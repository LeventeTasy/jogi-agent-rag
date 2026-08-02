import os, sys
import pandas as pd
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))


if project_root not in sys.path:
    sys.path.append(project_root)
from src.jogi_agent.flow import JogiFlow

BASE_DIR = Path(__file__).resolve().parent
PATH = BASE_DIR.parent / "datasets" / "answered_questions_agent_chunk.xlsx"
SAVE_PATH = BASE_DIR.parent / "results" / "answered_questions_agent_chunk.xlsx"

COLUMNS = [
    "Torveny", "Tipus", "Kerdes", "Q_chunk", "A_chunk",
    "Valasz", "Faithfulness", "Faithfulness_Reason", "Answer_Relevancy", "Answer_Relevancy_Reason", "Context_Relevancy","Context_Relevancy_Reason" ,
    "Summarization", "Summarization_Reason" , "Coherance", "Coherance_Reason","Toxicity", "Toxicity_Reason","Bias", "Bias_Reason" # osszesen: 20 oszlop
    # str, str, str, str, str, str, float, str, float, str, float, str, float, str, float, str, float, str, float, str
]

if os.path.exists(SAVE_PATH):
    df = pd.read_excel(SAVE_PATH)
else:
    df = pd.read_excel(PATH)


text_columns = [
        "Valasz",
        "A_chunk",
        "Q_chunk",
        "Faithfulness_Reason",
        "Answer_Relevancy_Reason",
        "Context_Relevancy_Reason",
        "Summarization_Reason",
        "Coherance_Reason",
        "Toxicity_Reason",
        "Bias_Reason",
    ]

for col in text_columns:
    df[col] = df[col].astype("string")

print(f"{len(df)} tesztkérdés beolvasva!")
print(df.head())

limit = 3
ind = 0

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
            "topic": kerdes,
            "details": ""
        }

    flow = JogiFlow()
    flow.state["inputs"] = inputs

    answer = str(flow.kickoff())
    print(answer+"\n\n")
    chunks_list = flow.get_chunks()
    print(chunks_list)
    a_chunk_string = "\n\n".join(chunks_list)

    uj_valasz = f"Sikeresen generált válasz a(z) {index}. sorhoz!"

    df.at[index, 'Valasz'] = answer
    df.at[index, 'A_chunk'] = a_chunk_string

    df.to_excel(SAVE_PATH, index=False)

    ind+=1



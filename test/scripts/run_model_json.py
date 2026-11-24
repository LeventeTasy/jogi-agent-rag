import ast
from datetime import datetime
from pathlib import Path

import pandas as pd
import os, time

from jogi_agent.router import RouterFlow

BASE_DIR = Path(__file__).resolve().parent
PATH = BASE_DIR.parent / "datasets" / "kerdesbank.json"
PATH_SAVE = BASE_DIR.parent / "results" / "json_kerdesbank.csv"




def run_model():
    df = pd.read_json(PATH)
    # df["a_chunk"], df["difference"], df["answer"] = None, None, None
    print(f"{len(df)} tesztkérdés beolvasva!")

    chatID = f"T_{datetime.now().strftime("%Y-%m-%d %H:%M:%S").upper()}"


    limit = 100
    ind = 0

    for index, row in df.iterrows():

        if ind >= limit:
            break

        jelenlegi_valasz = row['answer']
        jelenlegi_achunk = row['a_chunk']

        valasz_ures = pd.isna(jelenlegi_valasz) or str(jelenlegi_valasz).strip() == ""
        achunk_ures = pd.isna(jelenlegi_achunk) or str(jelenlegi_achunk).strip() == ""

        if not valasz_ures and not achunk_ures:
            print(f"Sor [{index}] már ki van töltve, kihagyás.")
            continue

        kerdes = row['input']
        print(f"Sor [{index}]: Feldolgozás alatt... Kérdés: '{kerdes[:50]}...'")

        inputs = {
                'topic': kerdes,
                'history': "",
                'pdf_text': "",
                'details': "",
                'da_questions': "",
                'da_answers': "",
                'username': "T_1",
                "chatID": chatID,
                "questionNumber": index
            }


        start_time = time.perf_counter()
        flow = RouterFlow()
        flow.state["inputs"] = inputs

        answer = str(flow.kickoff())
        elapsed_time = time.perf_counter() - start_time

        print(answer+"\n\n")
        chunks_list = flow.get_chunks()
        a_chunk_string = "\n\n".join(chunks_list)

        verifier_retries = flow.get_verifier_counter()
        questionID = flow.get_question_id()
        metrics = flow.get_metrics()

        df.at[index, 'a_chunk'] = a_chunk_string
        df.at[index, 'answer'] = answer
        df.at[index, 'Total_Tokens'] = metrics["totalTokens"]
        df.at[index, 'Prompt_Tokens'] = metrics["promptTokens"]
        df.at[index, 'Completion_Tokens'] = metrics["completionTokens"]
        df.at[index, 'Successful_Requests'] = metrics["successfulRequests"]

        df.at[index, "Verifier_Agent_Runs"] = int(verifier_retries)
        df.at[index, "Question_ID"] = questionID

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        uj_valasz = f"Sikeresen generált válasz a(z) {index}. sorhoz!"

        df.at[index, 'Runtime'] = elapsed_time
        df.at[index, "Timestamp"] = timestamp

        df.to_csv(PATH_SAVE, index=False, encoding="utf-8-sig")

        ind+=1

def run_eval():
    absz = False
    df = pd.read_csv(PATH_SAVE)
    print(f"{len(df)} tesztkérdés beolvasva!")

    df["difference"] = df["difference"].apply(
        lambda x: ast.literal_eval(x) if pd.notna(x) and str(x).strip() != "" else [])

    arr = []

    for index, row in df.iterrows():
        tartalom = row["difference"]
        for i in tartalom:
            arr.append(i)

    hossz = len(arr)
    ser = pd.Series(arr)

    if absz:
        for s, i in enumerate(arr):
            if type(i) == int:
                arr[s] = abs(i)

    #print(ser.value_counts())
    szazalek = (pd.Series(arr).value_counts(normalize=True) * 100).round(2)
    print(szazalek)

    nullak = sum(1 for elem in arr if str(elem).strip() == "0")

    print(f'Accuracy: {nullak/hossz}')

    """
    abszolútban:
    0: 50.35%
    1-3: 20.28%
    4-6: 5.6%
    7-9: 2.1%
    10: 0.35%
    
    x: 15.73%
    y: 4.55%
    !, (!), - = 0.35%, 0.35%, 0.35%
    
    """


run_eval()






















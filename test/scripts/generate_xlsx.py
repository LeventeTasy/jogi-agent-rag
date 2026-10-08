import ast
import pandas as pd
import random
from src.rag import build_rag
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import time
import json
from crewai import LLM

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = "models/" + str(os.getenv("EMBEDDINGS_GOOGLE_GENERATIVE_AI_MODEL_NAME"))

columns = [
    "Torveny", "Tipus", "Kerdes", "Q_chunk", "A_chunk",
    "Valasz", "Faithfulness", "Faithfulness_Reason", "Answer_Relevancy", "Answer_Relevancy_Reason",
    "Context_Relevancy", "Context_Relevancy_Reason", "Question_ID", "Runtime", "Timestamp",
    "Total_Tokens", "Prompt_Tokens", "Completion_Tokens", "Successful_Requests"
]

MODEL = "gemini/gemini-3.8-flash"
VALIDATOR_MODEL = "gemini/gemini-3.8-flash"

llm = LLM(model=MODEL)
validator_llm = LLM(model=VALIDATOR_MODEL)


def add_save_df(law, tipus_rovid, kerdes, rag_context):
    BASE_DIR = Path(__file__).resolve().parent
    file_path = BASE_DIR.parent / "datasets" / "full_test_questions.csv"

    extended_data = (
        law, tipus_rovid, kerdes, rag_context,
        None, None, None, None, None, None,
        None, None, None, None, None, None,
        None, None, None
    )

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df2 = pd.DataFrame([extended_data], columns=columns)
        df = pd.concat([df, df2], ignore_index=True)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
    else:
        df2 = pd.DataFrame([extended_data], columns=columns)
        df2.to_csv(file_path, index=False, encoding="utf-8-sig")


def validate_question(law, tipus, kerdes, chunk):
    PROMPT = f"""
        Ellenőrizd az alábbi magyar jogi tesztkérdést.
        
        Törvény: {law}
        Kategória: {tipus}
        
        Kérdés:
        {kerdes}
        
        A kérdéshez tartozó jogszabályi szöveg:
        {chunk}
        
        Döntsd el, hogy a kérdés megfelelő-e.
        
        Ezeket vizsgáld:
        - A kérdés egyértelmű és természetes?
        - A kérdés megválaszolható a megadott jogszabályi szövegből?
        - A szükséges információ ténylegesen benne van a szövegben?
        - Nem igényel külső jogi ismeretet?
        - A kérdés megfelel a megadott nehézségi kategóriának?
        - Nem tartalmaz olyan feltételezést, amely nincs benne a forrásban?
        
        Három lehetőség van:
        
        APPROVE = megfelelő
        MODIFY = alapvetően jó, de módosítani kell
        REJECT = nem használható
        
        Kizárólag ebben a formában válaszolj:
        {{"decision": "APPROVE", "question": "kérdés", "reason": "rövid indoklás"}}
        """

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = validator_llm.call(PROMPT)

            response = response.replace("```json", "").replace("```", "").strip()

            result = json.loads(response)

            return result

        except Exception as e:
            print(f"Validator hiba: {e}")

            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise


PROJECT_SRC = Path(__file__).resolve().parent.parent.parent
db_path = str(PROJECT_SRC / "chroma_db")

if not Path(db_path).exists():
    print("ChromaDB generálása...")
    build_rag()
else:
    print("ChromaDB megtalálható...")

embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
db = Chroma(persist_directory=db_path, embedding_function=embeddings)

all_data = db.get()
all_docs = all_data["documents"]
all_metas = all_data["metadatas"]

torvenyek = [
    "Munka Törvénykönyve (Mt.)",
    "GDPR rendelet",
    "Polgári Törvénykönyv (Ptk.)",
    "SZJA törvény",
    "Büntető Törvénykönyv (Btk.)"
]


law_chunks_dict = {}

for law in torvenyek:
    chunks = [
        all_docs[i]
        for i in range(len(all_docs))
        if all_metas[i] is not None and law in str(all_metas[i].get("law", ""))
    ]

    law_chunks_dict[law] = chunks


# 1. fazis: torvenyenkent 8 konnyu es 8 nehez kerdes

kategoriak = {
    "könnyű": 10,
    "nehéz": 6
}


for law, chunks in law_chunks_dict.items():
    if not chunks:
        print(f"Nincs chunk ehhez: {law}")
        continue

    print(f"\n{law} feldolgozása...")

    for tipus_rovid, db_szam in kategoriak.items():
        print(f"\n{db_szam} db {tipus_rovid} kérdés generálása...")

        chunks2 = chunks.copy()
        random.shuffle(chunks2)

        generated = 0
        chunk_index = 0

        while generated < db_szam and chunk_index < len(chunks2):
            rag_context = chunks2[chunk_index]
            chunk_index += 1

            if tipus_rovid == "könnyű":
                nehezseg = """
                        A kérdés egy konkrét jogszabályi szabály közvetlen alkalmazását
                        vagy felismerését igényelje. Ne legyen szükség több különálló
                        szabály összekapcsolására.
                        """
            else:
                nehezseg = """
                        A kérdés legyen összetettebb, és tartalmazzon valamilyen
                        feltételt, kivételt, speciális esetet vagy összetettebb
                        élethelyzetet. Ettől függetlenül kizárólag a megadott
                        jogszabályi szövegből legyen megválaszolható.
                        """

            PROMPT = f"""
                        Generálj egyetlen magyar jogi tesztkérdést a következő törvényből:
                        
                        {law}
                        
                        A kérdés nehézsége:
                        {nehezseg}
                        
                        Kizárólag az alábbi jogszabályi szöveget használd:
                        
                        {rag_context}
                        
                        Fontos:
                        - A kérdés természetesen hangozzon, mintha egy ember tenné fel.
                        - A kérdésre a megadott szöveg alapján lehessen válaszolni.
                        - Ne használj a forrásban nem szereplő jogi információt.
                        - Ne legyen cross-domain kérdés.
                        
                        Csak a kérdést írd ki, semmi mást.
                        """

            try:
                response = llm.call([
                    {"role": "user", "content": PROMPT}
                ])

                kerdes = response.strip().replace("```", "").strip()

                validation = validate_question(law, tipus_rovid, kerdes, rag_context)

                decision = validation["decision"].upper()

                print(f"\nGenerált kérdés: {kerdes}")
                print(f"Validator: {decision}")
                print(f"Indoklás: {validation['reason']}")

                if decision == "REJECT":
                    print("Elutasítva.")
                    continue

                if decision == "MODIFY":
                    kerdes = validation["question"]

                add_save_df(law, tipus_rovid, kerdes, rag_context)

                generated += 1

                print(f"Elmentve ({generated}/{db_szam})")

            except Exception as e:
                print(f"Hiba: {e}")


# 2. fazis: cross-domain kérdések

print("\nÖsszetett kérdések generálása...")

law_pairs = []

for i in range(len(torvenyek)):
    for j in range(i + 1, len(torvenyek)):
        law_pairs.append((torvenyek[i], torvenyek[j]))


for law1, law2 in law_pairs:
    print(f"\n{law1} + {law2}")

    generated = 0

    while generated < 2:
        chunk1 = random.choice(law_chunks_dict[law1])
        chunk2 = random.choice(law_chunks_dict[law2])

        rag_context = f"""
            Első jogterület:
            {law1}
            
            {chunk1}
            
            Második jogterület:
            {law2}
            
            {chunk2}
            """

        PROMPT = f"""
            Generálj egyetlen összetett, magyar nyelvű jogi szituációs kérdést.
            
            A kérdéshez szükség legyen mindkét jogterület szabályára:
            
            {law1}
            {law2}
            
            Kizárólag az alábbi jogszabályi részekből dolgozz:
            
            {rag_context}
            
            A kérdés legyen valódi élethelyzetet bemutató, természetes
            és összetett.
            
            Mindkét jogterületnek ténylegesen szükségesnek kell lennie
            a kérdés megválaszolásához.
            
            Ha az egyik jogterület elhagyásával is megválaszolható lenne
            a kérdés, akkor az nem megfelelő.
            
            Csak a kérdést írd ki.
            """

        try:
            response = llm.call(PROMPT)

            kerdes = response.strip().replace("```", "").strip()

            validation_prompt = f"""
            Ellenőrizd az alábbi cross-domain jogi tesztkérdést.
            
            Első jogterület:
            {law1}
            
            Forrás:
            {chunk1}
            
            Második jogterület:
            {law2}
            
            Forrás:
            {chunk2}
            
            Kérdés:
            {kerdes}
            
            Csak akkor fogadd el, ha:
            - mindkét jogterület szükséges a válaszhoz,
            - mindkét forrás tartalmazza a szükséges információt,
            - nem kell külső jogi ismeret,
            - a kérdés természetes és egyértelmű.
            
            Válasz:
            {{"decision": "APPROVE", "question": "kérdés", "reason": "indoklás"}}
            
            A decision értéke APPROVE, MODIFY vagy REJECT lehet.
            """

            validation = validate_question(
                f"{law1}; {law2}",
                "összetett",
                kerdes,
                rag_context
            )

            decision = validation["decision"].upper()

            print(f"Kérdés: {kerdes}")
            print(f"Validator: {decision}")
            print(f"Indoklás: {validation['reason']}")

            if decision == "REJECT":
                continue

            if decision == "MODIFY":
                kerdes = validation["question"]

            add_save_df(
                f"{law1}; {law2}",
                "összetett",
                kerdes,
                rag_context
            )

            generated += 1

            print(f"Elmentve ({generated}/2)")

        except Exception as e:
            print(f"Hiba: {e}")
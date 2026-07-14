import ast
import pandas as pd
import random
from litellm import completion
from typing import Tuple
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import time
from litellm.exceptions import ServiceUnavailableError

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = str(os.getenv("MODEL"))
EMBEDDING_MODEL = "models/" + str(os.getenv("EMBEDDINGS_GOOGLE_GENERATIVE_AI_MODEL_NAME"))

columns = [
    "Torveny", "Tipus", "Kerdes", "Q_chunk", "A_chunk",
    "Valasz", "Groundedness", "Groundedness_Reason", "Context_Relevance", "Answer_Relevance"
]

df = pd.DataFrame(columns=columns)

def add_save_df(new_data: Tuple[str, str, str, int, str, int, str]):
    global df

    df2 = pd.DataFrame([new_data], columns=df.columns)

    df = pd.concat([df, df2], ignore_index=True)

    df.to_excel('test_questions.xlsx', index=False)

#add_save_df(("test2", "test2", "test2", 1, "test2", 1, "test2"))

def save_to_excel(df):
    file_path = 'generated_test_questions.xlsx'

    if os.path.exists(file_path):
        print(f"\nMeglévő fájl észlelve: {file_path}")

        existing_df = pd.read_excel(file_path)

        final_df = pd.concat([existing_df, df], ignore_index=True)

        final_df.to_excel(file_path, index=False)
        print(f"Az adatok hozzáfűzve a fájlhoz!")

    else:
        df.to_excel(file_path, index=False)
        print(f"Új fájl létrehozva: {file_path}")

db_path = os.path.abspath(os.path.join(os.getcwd(), "../chroma_db"))
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
db = Chroma(persist_directory=db_path, embedding_function=embeddings)

all_data = db.get()
all_docs = all_data['documents']
all_metas = all_data['metadatas']

torvenyek = [
    "Munka Törvénykönyve (Mt.)",
    "GDPR rendelet",
    "Polgári Törvénykönyv (Ptk.)",
    "SZJA törvény"
]


law_chunks_dict = {}
for law in torvenyek:
    chunks = [
        all_docs[i] for i in range(len(all_docs))
        if all_metas[i] is not None and law in str(all_metas[i].get('law', ''))
    ]
    law_chunks_dict[law] = chunks

#print(law_chunks_dict)


# 1. fazis: torvenyenkent 15 konnyu és 5 nehez kerdes
kategoriak = {
    "könnyű, alapvető, egyenes választ igénylő": 15,
    "nehéz, kivételekre és speciális esetekre fókuszáló": 5
}

print("\n--- 1. FÁZIS: SZOLID JOGÁGI KÉRDÉSEK GENERÁLÁSA ---")
for law, chunks in law_chunks_dict.items():
    if not chunks:
        print(f"Nincs chunk ehhez: {law}")
        continue

    print(f"\n{law} feldolgozása...")

    for nehezseg, db_szam in kategoriak.items():
        print(f"  🔥 Generálok {db_szam} db {nehezseg.split(',')[0]} kérdést...")

        sample_size = min(15, len(chunks))
        random_chunks = random.sample(chunks, sample_size)
        rag_context = "\n\n".join(random_chunks)

        PROMPT = f"""
        Feladatod, hogy generálj pontosan {db_szam} darab egyedi, realisztikus magyar jogi kérdést (élethelyzetet) a következő törvény alapján: {law}.
        A kérdések nehézsége ilyen legyen: {nehezseg}.

        KIZÁRÓLAG AZ ALÁBBI JOGSZABÁLYI SZÖVEGEK ALAPJÁN DOLGOZZ:
        {rag_context}

        KÖTELEZŐ KIMENETI FORMÁTUM:
        Kizárólag egy darab érvényes Python listát adj vissza markdown kódblokkban, amely pontosan {db_szam} string elemet tartalmaz. Semmi más szöveget ne írj!
        """


        max_retries = 3
        attempt = 0
        success = False

        while attempt < max_retries and not success:
            try:
                response = completion(
                    model="gemini-2.5-flash",
                    messages=[{"role": "user", "content": PROMPT}],
                    api_key=API_KEY
                )
                success = True

                try:
                    uj_kerdesek = ast.literal_eval(clean_output)
                    for kerdes in uj_kerdesek:
                        tipus_rovid = nehezseg.split(',')[0]
                        df.loc[len(df)] = [law, tipus_rovid, kerdes, rag_context, None, None, None, None, None, None]
                    print(f"{len(uj_kerdesek)} kérdés elmentve!")
                except Exception as e:
                    print(f"Hiba történt: {e}")

            except ServiceUnavailableError:
                attempt += 1
                print(f"503 error, próbálkozás {attempt}/{max_retries}... várjunk 10 mp-et!")
                time.sleep(10)
                if attempt == max_retries:
                    print(" Túl sok hiba, átlépés")
                    raise

        clean_output = response['choices'][0]['message']['content'].replace("```python", "").replace("```", "").strip()





# 2. fazis: 20 db osszetett kerdes
print("\n--- 2. FÁZIS: CROSS-DOMAIN BOSS BATTLE (20 DB) ---")

for i in range(4):
    print(f"{i + 1}. 5 db összetett kérdés generálása...")

    mixed_chunks = []
    for law, chunks in law_chunks_dict.items():
        if chunks:
            mixed_chunks.extend(random.sample(chunks, min(3, len(chunks))))

    random.shuffle(mixed_chunks)
    rag_context = "\n\n".join(mixed_chunks)

    CROSS_DOMAIN_PROMPT = f"""
    Feladatod, hogy generálj pontosan 5 darab nagyon összetett, csavaros magyar jogi szituációs kérdést.
    FONTOS SZABÁLY: Minden egyes kérdésnek olyan élethelyzetet kell bemutatnia, amelynek a megoldásához 
    LEGALÁBB KÉT KÜLÖNBÖZŐ JOGTERÜLETRE (pl. Munkajog ÉS Adatvédelem, vagy Polgári jog ÉS Adózás) is szükség van!

    KIZÁRÓLAG AZ ALÁBBI ÖSSZEMIXELT JOGSZABÁLYI SZÖVEGEK ALAPJÁN DOLGOZZ:
    {rag_context}

    KÖTELEZŐ KIMENETI FORMÁTUM:
    Kizárólag egy darab érvényes Python listát adj vissza markdown kódblokkban, amely pontosan 5 string elemet tartalmaz. Semmi más szöveget ne írj!
    """

    max_retries = 3
    attempt = 0
    success = False

    while attempt < max_retries and not success:
        try:
            response = completion(
                model="gemini-2.5-flash",
                messages=[{"role": "user", "content": PROMPT}],
                api_key=API_KEY
            )
            success = True

            clean_output = response['choices'][0]['message']['content'].replace("```python", "").replace("```",
                                                                                                         "").strip()

            try:
                uj_kerdesek = ast.literal_eval(clean_output)
                for kerdes in uj_kerdesek:
                    df.loc[len(df)] = ["Kombinált", "összetett", kerdes, rag_context, None, None, None, None, None,
                                       None]
                print(f"✅ {len(uj_kerdesek)}kérdés elmentve!")
            except Exception as e:
                print(f"Hiba történt: {e}")

        except ServiceUnavailableError:
            attempt += 1
            print(f"Hiba, próbálkozás {attempt}/{max_retries}... várjunk 10 mp-et!")
            time.sleep(10)
            if attempt == max_retries:
                print("Túl sok hiba, következő")
                raise

save_to_excel(df)



















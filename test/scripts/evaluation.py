import os
import pandas as pd
from pathlib import Path


def evaluate(path1: str, path2: str):
    if os.path.exists(path1) and os.path.exists(path2):
        if "xlsx" in str(path1):
            df = pd.read_excel(path1, index_col=0)
        elif "csv" in str(path1):
            df = pd.read_csv(path1, index_col=0)

        if "xlsx" in str(path2):
            df2 = pd.read_excel(path2, index_col=0)
        elif "csv" in str(path2):
            df2 = pd.read_csv(path2, index_col=0)

        metrics = [
            "Faithfulness",
            "Answer_Relevancy",
            "Context_Relevancy",
        ]

        print("="*50)
        print("Első adatbázis átlagai:")
        hallucination_1 = round((1-df["Faithfulness"].mean())*100,2)
        print(f"Hallucináció\t{hallucination_1}%")
        atl_elso = df[metrics].mean()
        print(atl_elso)
        print(f"Átlagos runtime\t {round(df['Runtime'].mean(), 2)}s")
        if "Verifier_Agent_Runs" in df.columns:
            print(f"Verifier Agent lefutott {df['Verifier_Agent_Runs'].mean()}x")
        if "Total_Tokens" in df.columns:
            print(f"Avg. total tokens: {round(df['Total_Tokens'].mean(), 2)}x")
        print("-"*30)
        print(f"Összes kérdés\t{df['Faithfulness'].count()}")
        print()

        print("=" * 50)
        print("Második adatbázis átlagai:")
        hallucination_2 = round((1 - df2["Faithfulness"].mean())*100, 2)
        print(f"Hallucináció\t{hallucination_2}%")
        atl_masodik = df2[metrics].mean()
        print(atl_masodik)
        print(f"Átlagos runtime\t {round(df2['Runtime'].mean(), 2)}s")
        if "Verifier_Agent_Runs" in df2.columns:
            print(f"Verifier Agent lefutott {df2['Verifier_Agent_Runs'].mean()}x")
        if "Total_Tokens" in df2.columns:
            print(f"Avg. total tokens: {round(df2['Total_Tokens'].mean(), 2)}x")
        print("-" * 30)
        print(f"Összes kérdés\t{df2['Faithfulness'].count()}")
        print()

        print("=" * 50)
        print("Különbség\t (1.-2.)")
        print(f"Hallucináció\t {hallucination_1-hallucination_2}%")
        kulonbseg = atl_elso-atl_masodik
        print(kulonbseg)
        print()

        minuszok = []
        pozitivok = []
        for i in kulonbseg:
            if i < 0:
                minuszok.append(abs(i))
            elif i > 0:
                pozitivok.append(i)

        if len(minuszok) != 0 and len(pozitivok) != 0:
            if sum(minuszok)/len(minuszok) > sum(pozitivok)/len(pozitivok):
                print(f"Átlagban a második adatbázis erősebb, ennyivel: {sum(minuszok)/len(minuszok):.2%}")
            elif sum(minuszok)/len(minuszok) < sum(pozitivok)/len(pozitivok):
                print(f"Átlagban a második adatbázis erősebb, ennyivel: {sum(pozitivok) / len(pozitivok):.2%}")
        elif len(minuszok) == 0 and len(pozitivok) != 0:
            print(f"Első adatbázis jobb, átlagban ennyivel: {sum(pozitivok) / len(pozitivok):.2%}")
        elif len(minuszok) != 0 and len(pozitivok) == 0:
            print(f"Második adatbázis jobb, átlagban ennyivel: {sum(minuszok) / len(minuszok):.2%}")
    else:
        raise FileNotFoundError

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    PATH1 = BASE_DIR.parent / "results" / "model_comparison" / "answered_questions_agent_wo_ver+gro.csv"
    PATH2 = BASE_DIR.parent / "results" / "model_comparison" / "answered_questions_agent_unified_grounding.csv"

    evaluate(PATH1, PATH2)
import os
import pandas as pd
from pathlib import Path


def evaluate(path1: str, path2: str):
    if os.path.exists(path1) and os.path.exists(path2):
        df = pd.read_excel(path1, index_col=0)
        df2 = pd.read_excel(path2, index_col=0)

        metrics = [
            "Faithfulness",
            "Answer_Relevancy",
            "Context_Relevancy",
            "Coherance"
        ]

        print("="*50)
        print("Első adatbázis átlagai:")
        atl_elso = df[metrics].mean()
        print(atl_elso)
        print()

        print("=" * 50)
        print("Második adatbázis átlagai:")
        atl_masodik = df2[metrics].mean()
        print(atl_masodik)
        print()

        print("=" * 50)
        print("Különbség: (1.-2.)")
        kulonbseg = atl_elso-atl_masodik
        print(kulonbseg)

        minuszok = []
        pozitivok = []
        for i in kulonbseg:
            if i < 0:
                minuszok.append(abs(i))
            elif i > 0:
                pozitivok.append(i)

        if len(minuszok) != 0 or len(pozitivok) != 0:
            if sum(minuszok)/len(minuszok) > sum(pozitivok)/len(pozitivok):
                print(f"Átlagban a második adatbázis erősebb, ennyivel: {sum(minuszok)/len(minuszok)}")
            elif sum(minuszok)/len(minuszok) < sum(pozitivok)/len(pozitivok):
                print(f"Átlagban a második adatbázis erősebb, ennyivel: {sum(pozitivok) / len(pozitivok)}")
        elif len(minuszok) == 0 and len(pozitivok) != 0:
            print(f"Első adatbázis jobb, átlagban ennyivel: {sum(pozitivok) / len(pozitivok)}")
        elif len(minuszok) != 0 and len(pozitivok) == 0:
            print(f"Második adatbázis jobb, átlagban ennyivel: {sum(minuszok) / len(minuszok)}")
    else:
        raise FileNotFoundError

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    PATH1 = BASE_DIR.parent / "results" / "answered_questions.xlsx"
    PATH2 = BASE_DIR.parent / "results" / "answered_questions_agent_chunk.xlsx"

    evaluate(PATH1, PATH2)
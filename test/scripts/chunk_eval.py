from pathlib import Path

import pandas as pd
import os, time

BASE_DIR = Path(__file__).resolve().parent
PATH = BASE_DIR.parent / "results" / "json_kerdesbank.csv"

df = pd.read_csv(PATH)
df["difference"] = df["difference"].astype(object)
print(f"Database hossza: {len(df)}")
inp = ""

for index, row in df.iterrows():
    jelenlegi_diff = row['difference']

    diff_ures = pd.isna(jelenlegi_diff) or str(jelenlegi_diff).strip() == ""

    if not diff_ures:
        print(f"Sor [{index}] már ki van töltve, kihagyás.")
        continue

    print(f"Index: {index}")
    print(f'References:\n{row["references"]}')
    print("-" * 25)
    print(f"A_Chunk:\n{row['a_chunk']}")

    inp = input(": ")

    if inp != "break":
        arr = inp.strip().split(",")
        for s, i in enumerate(arr):
            try:
                arr[s] = int(i)
            except ValueError:
                arr[s] = str(i)

        df.at[index, "difference"] = arr
    else:
        break

    df.to_csv(PATH, index=False, encoding="utf-8-sig")
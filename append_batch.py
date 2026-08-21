"""
Mo phong viec thu thap them du lieu: gop train_batch2.csv vao train_batch1.csv.
"""

import os

import pandas as pd

DATA_DIR = "data"
BATCH1_PATH = os.path.join(DATA_DIR, "train_batch1.csv")
BATCH2_PATH = os.path.join(DATA_DIR, "train_batch2.csv")


def main() -> None:
    df1 = pd.read_csv(BATCH1_PATH)
    df2 = pd.read_csv(BATCH2_PATH)

    before = len(df1)
    combined = pd.concat([df1, df2], ignore_index=True)
    combined.to_csv(BATCH1_PATH, index=False)

    print(f"Cap nhat du lieu: {before} -> {len(combined)} mau")


if __name__ == "__main__":
    main()

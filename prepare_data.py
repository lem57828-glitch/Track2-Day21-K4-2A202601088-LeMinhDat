"""
Tai va chuan bi bo du lieu Adult / Census Income (UCI).

Tao ba file trong data/:
    train_batch1.csv, holdout.csv, train_batch2.csv
"""

import os
import urllib.request

import pandas as pd

RAW_COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country",
    "target",
]

FEATURES = [
    "age", "workclass", "education_num", "marital_status", "occupation",
    "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week",
]

CATEGORICAL_COLUMNS = ["workclass", "marital_status", "occupation", "relationship", "sex"]

TRAIN_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
TEST_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test"

DATA_DIR = "data"
HOLDOUT_SIZE = 500
RANDOM_STATE = 42


def _download(url: str, path: str) -> None:
    if os.path.exists(path):
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(path, "wb") as f:
        f.write(resp.read())


def _load_raw() -> pd.DataFrame:
    train_raw = os.path.join(DATA_DIR, "_adult.data")
    test_raw = os.path.join(DATA_DIR, "_adult.test")
    _download(TRAIN_URL, train_raw)
    _download(TEST_URL, test_raw)

    df_train = pd.read_csv(
        train_raw, header=None, names=RAW_COLUMNS,
        skipinitialspace=True, na_values="?",
    )
    df_test = pd.read_csv(
        test_raw, header=None, names=RAW_COLUMNS,
        skipinitialspace=True, na_values="?", skiprows=1,
    )
    df_test["target"] = df_test["target"].str.rstrip(".")

    return pd.concat([df_train, df_test], ignore_index=True)


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    df = _load_raw()
    df = df.dropna()
    df = df[FEATURES + ["target"]].copy()

    for col in CATEGORICAL_COLUMNS:
        mapping = {cat: i for i, cat in enumerate(sorted(df[col].unique()))}
        df[col] = df[col].map(mapping)

    df["target"] = (df["target"].str.strip() == ">50K").astype(int)

    df = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)

    holdout = df.iloc[:HOLDOUT_SIZE]
    remaining = df.iloc[HOLDOUT_SIZE:]
    half = len(remaining) // 2
    train_batch1 = remaining.iloc[:half]
    train_batch2 = remaining.iloc[half:]

    train_batch1.to_csv(os.path.join(DATA_DIR, "train_batch1.csv"), index=False)
    holdout.to_csv(os.path.join(DATA_DIR, "holdout.csv"), index=False)
    train_batch2.to_csv(os.path.join(DATA_DIR, "train_batch2.csv"), index=False)

    print(f"train_batch1.csv : {len(train_batch1)} mau")
    print(f"holdout.csv      : {len(holdout)} mau")
    print(f"train_batch2.csv : {len(train_batch2)} mau")
    print(f"Ty le lop >50K   : {df['target'].mean() * 100:.1f}%")


if __name__ == "__main__":
    main()

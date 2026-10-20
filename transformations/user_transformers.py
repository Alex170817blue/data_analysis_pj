
import pandas as pd


def transform_users(df: pd.DataFrame) -> pd.DataFrame:
    """Pulisce e normalizza il DataFrame degli utenti."""

    df = df.copy()

    # ID numerico
    df["UserID"] = pd.to_numeric(
        df["UserID"], errors="raise"
    ).astype("int64")

    # Manteniamo Age come valore numerico originale
    df["Age"] = pd.to_numeric(
        df["Age"], errors="raise"
    ).astype("int64")

    # CAP come testo, per preservare eventuali zeri iniziali
    df["CAP"] = df["CAP"].astype("string").str.strip()

    # Normalizzazione dei campi testuali
    for column in ["Gender", "Work"]:
        df[column] = df[column].astype("string").str.strip()

    return df[["UserID", "Gender", "Age", "CAP", "Work"]]

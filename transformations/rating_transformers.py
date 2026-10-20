
import pandas as pd


def transform_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Pulisce le valutazioni e converte il timestamp in data UTC."""

    df = df.copy()

    for column in ["UserID", "MovieID", "Rating", "Timestamp"]:
        df[column] = pd.to_numeric(
            df[column], errors="raise"
        ).astype("int64")

    # Unix timestamp in secondi -> data e ora UTC
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        unit="s",
        origin="unix",
        utc=True,
        errors="raise",
    )

    return df[["UserID", "MovieID", "Rating", "Timestamp"]]

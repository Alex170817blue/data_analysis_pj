
import pandas as pd


def transform_movies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    required_columns = {"MovieID", "Title", "Genres"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonne mancanti: {sorted(missing_columns)}"
        )

    # Correzione del film Casino: MovieID 16, anno 1995
    movie_ids = pd.to_numeric(df["MovieID"], errors="coerce")
    casino_mask = movie_ids.eq(16)

    if casino_mask.sum() != 1:
        raise ValueError(
            "Atteso un solo film con MovieID 16."
        )

    df.loc[casino_mask, "Title"] = "Casino (1995)"

    # Correzione del titolo mancante
    blank_title = (
        df["Title"].isna()
        | df["Title"].astype("string").str.strip().eq("").fillna(False)
    )

    if blank_title.sum() > 1:
        raise ValueError(
            "Sono presenti più titoli mancanti. "
            "Identificare il MovieID corretto."
        )

    if blank_title.sum() == 1:
        df.loc[blank_title, "Title"] = "Phantom of the Opera, The"

    # Estrazione dell'anno dal titolo
    extracted_year = (
        df["Title"]
        .astype("string")
        .str.extract(r"\((\d{4})\)\s*$", expand=False)
    )

    year = pd.to_numeric(extracted_year, errors="coerce")

    df["YEAR"] = year.where(
        year.between(1870, 2100)
    ).astype("Int64")

    # Rimozione dell'anno dal titolo
    valid_year = df["YEAR"].notna()

    df.loc[valid_year, "Title"] = (
        df.loc[valid_year, "Title"]
        .str.replace(r"\s*\(\d{4}\)\s*$", "", regex=True)
        .str.strip()
    )

    # Correzione delle anomalie nei generi
    df["Genres"] = (
        df["Genres"]
        .astype("string")
        .str.replace("Dramatic", "Drama", regex=False)
        .str.replace("Dramma", "Drama", regex=False)
        .str.replace("Comedy--Horror", "Comedy|Horror", regex=False)
        .str.replace("–", "|", regex=False)
        .str.replace("—", "|", regex=False)
    )

    return df

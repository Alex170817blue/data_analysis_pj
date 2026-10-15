import re
import pandas as pd

'''separiamo la data dal titolo '''

def transform_movies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    extracted_year = df["Title"].str.extract(
        r"\((\d{4})\)\s*$",
        expand=False,
    )

    year = pd.to_numeric(extracted_year, errors="coerce")
    df["year"] = year.where(year.between(1870, 2100)).astype("Int64")
    valid_year = df["year"].notna()
    df.loc[valid_year, "Title"] = (
        df.loc[valid_year, "Title"].str.replace(
            r"\s*\(\d{4}\)$",
            "",
            regex=True
        )
    )
    return df
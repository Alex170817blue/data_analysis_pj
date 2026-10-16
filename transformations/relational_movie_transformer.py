
import pandas as pd

from transformations.film_transformers import transform_movies


def transform_movies_relational(df: pd.DataFrame,) -> dict[str, pd.DataFrame]:
    # Riutilizza la pulizia che hai già implementato
    movies_clean = transform_movies(df.copy())

    # Garantisce un ID numerico per ogni film
    movies_clean["MovieID"] = pd.to_numeric(
        movies_clean["MovieID"],
        errors="raise",
    ).astype("int64")

    # Tabella movies: solo gli attributi del film
    movies = movies_clean[
        ["MovieID", "Title", "YEAR"]
    ].copy()

    # Una riga per ogni coppia film-genere
    movie_genres = (
        movies_clean[["MovieID", "Genres"]]
        .assign(
            Genres=lambda data: data["Genres"]
            .astype("string")
            .str.split("|", regex=False)
        )
        .explode("Genres")
        .rename(columns={"Genres": "Name"})
    )

    movie_genres["Name"] = (
        movie_genres["Name"].astype("string").str.strip()
    )

    # Elimina valori vuoti e associazioni duplicate
    movie_genres = movie_genres.dropna(subset=["Name"])
    movie_genres = movie_genres[
        movie_genres["Name"].ne("")
    ].drop_duplicates(["MovieID", "Name"])

    # Tabella genres: elenco dei generi distinti
    genre_names = sorted(movie_genres["Name"].unique())

    genres = pd.DataFrame({
        "GenreID": range(1, len(genre_names) + 1),
        "Name": genre_names,
    })

    # Collega ogni nome al relativo GenreID
    genre_ids = genres.set_index("Name")["GenreID"]

    movie_genres["GenreID"] = (
        movie_genres["Name"].map(genre_ids).astype("int64")
    )

    movie_genres = movie_genres[
        ["MovieID", "GenreID"]
    ].reset_index(drop=True)

    return {
        "movies": movies.reset_index(drop=True),
        "genres": genres,
        "movie_genres": movie_genres,
    }

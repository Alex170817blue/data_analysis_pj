
import os

from config.sources import SOURCES
from readers.csv_reader import CSVReader
from transformations.film_transformers import transform_movies
from database import Database
from sql_connection import SQLConnection
from transformations.relational_movie_transformer import transform_movies_relational


def main():
    # Configurazione della sorgente
    config = SOURCES["movies"]

    reader = CSVReader(
        path=config["path"],
        has_header=config["has_header"],
        delimiter=config["delimiter"],
        encoding=config["encoding"],
    )

    # Caricamento e trasformazione in memoria
    db = Database()

    db.add_source(
        table_name="movies_clean",
        reader=reader,
        required_columns=["MovieID", "Title", "Genres"],
        transformer=transform_movies_relational,
    )

        # Recupero delle tabelle relazionali
    print("Tabelle caricate:", db.list_tables())

    movies = db.get_table("movies")
    genres = db.get_table("genres")
    movie_genres = db.get_table("movie_genres")

    print("Numero di film:", len(movies))
    print("Numero di generi:", len(genres))
    print("Numero di associazioni:", len(movie_genres))

    # Esporta il CSV dei film
    output_path = "data/movies_clean.csv"
    os.makedirs("data", exist_ok=True)

    movies.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )
    # Caricamento in MySQL
    sql = SQLConnection()

    try:
        sql.connect()

        # Prima i record principali
        db.write_to_sql(
            "movies", sql, if_exists="append"
        )
        db.write_to_sql(
            "genres", sql, if_exists="append"
        )

        # Poi le associazioni: i record referenziati esistono già
        db.write_to_sql(
            "movie_genres", sql, if_exists="append"
        )

        print("Esportazione SQL completata.")

    finally:
        sql.close()


    print(f"CSV pulito esportato in: {output_path}")

if __name__ == "__main__":
    main()


import os

from config.sources import SOURCES
from readers.csv_reader import CSVReader
from database import Database
from sql_connection import SQLConnection
from transformations.relational_movie_transformer import transform_movies_relational
from transformations.film_transformers import transform_movies

from dao.dao_genre import DaoGenre
from dao.dao_movie import DaoMovie

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

    print("Colonne movies:", movies.columns.tolist())
    print("Colonne genres:", genres.columns.tolist())
    print("Colonne movie_genres:", movie_genres.columns.tolist())

    # creazione csv per dao
    flat_movies = transform_movies(reader.read())

    output_path = "data/movies_clean.csv"
    os.makedirs("data", exist_ok=True)

    flat_movies.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    # Esporta il CSV dei film
    output_path = "data/movies_clean.csv"
    os.makedirs("data", exist_ok=True)

    flat_movies = transform_movies(reader.read())

    # Esporto anche la colonna Genres, necessaria ai DAO
    flat_movies.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"CSV pulito esportato in: {output_path}")

    #esporto i csv flat
    movies.to_csv(
    "data/movies.csv",
    index=False,
    encoding="utf-8-sig",
    )

    genres.to_csv(
        "data/genres.csv",
        index=False,
        encoding="utf-8-sig",
    )

    movie_genres.to_csv(
        "data/movie_genres.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("CSV relazionali esportati:")
    print("- data/movies.csv")
    print("- data/genres.csv")
    print("- data/movie_genres.csv")

    # Creazione dei DAO
    dao_genre = DaoGenre()
    dao_movie = DaoMovie(output_path, dao_genre)

    print("Film caricati nei DAO:", len(dao_movie.get_all_movies()))
    print("Generi caricati nei DAO:", len(dao_genre.get_all_genres()))

    movie = dao_movie.get_movie_by_id(16)
    print("Film con ID 16:", movie)

    if movie is not None:
        print("Generi del film:", movie.genres)

    genre = dao_genre.get_genre_by_name("Comedy")
    if genre is not None:
        print("Film di genere Comedy:", len(genre.movies))

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

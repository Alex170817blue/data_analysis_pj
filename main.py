
import os

from config.sources import SOURCES
from readers.csv_reader import CSVReader
from transformers.film_transformers import transform_movies
from database import Database
from sql_connection import SQLConnection


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
        transformer=transform_movies,
    )

    # Recupero della tabella pulita
    movies = db.get_table("movies_clean")

    # Controlli preliminari
    print("Tabelle caricate:", db.list_tables())
    print("Numero di film:", len(movies))
    print("Colonne:", movies.columns.tolist())

    # Esportazione del CSV pulito
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

        rows_written = db.write_to_sql(
            table_name="movies_clean",
            connection=sql,
            sql_table_name="movies_clean",
        )

        print(
            f"Caricamento MySQL completato: "
            f"{rows_written} righe inserite."
        )

    finally:
        sql.close()


    print(f"CSV pulito esportato in: {output_path}")


if __name__ == "__main__":
    main()

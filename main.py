from config.sources import SOURCES
from database import Database
from readers.csv_reader import CSVReader
from transformers.film_transformers import transform_movies

config = SOURCES["movies"]

csv_reader = CSVReader(
    path=config["path"],
    has_header=config["has_header"],
    delimiter=config["delimiter"],
    encoding=config["encoding"],
)

db = Database()

db.add_source("raw_movies", csv_reader, transformer= transform_movies)
movies = db.get_table("raw_movies")
print(movies.head())
import csv

from model import Genre, Movie


class DaoMovie:
    def __init__(self, csv_path, dao_genre):
        self.dao_genre = dao_genre
        self._movies_map = {}
        self._load_data(csv_path)

    def _load_data(self, csv_path):
        with open(csv_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                movie_id = int(row["MovieID"])
                title = row["Title"]

                year_str = row["YEAR"]
                year = int(year_str) if year_str and year_str.isdigit() else None

                movie = Movie(movie_id, title, year)
                self._movies_map[movie_id] = movie

                for name in row["Genres"].split("|"):
                    name = name.strip()
                    if not name:
                        continue

                    genre = self.dao_genre.get_genre_by_name(name)

                    if genre is None:
                        genre = Genre(name)
                        self.dao_genre.add_genre(genre)

                    movie.genres.append(genre)
                    genre.movies.append(movie)

    def get_movie_by_id(self, movie_id):
        return self._movies_map.get(movie_id)

    def get_all_movies(self):
        return list(self._movies_map.values())
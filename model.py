class Movie:
    def __init__(self, movie_id, title, year):
        self.movie_id = movie_id
        self.title = title
        self.year = year
        self.genres = []

    def __repr__(self):
        return f"Movie('{self.title}', {self.year})"


class Genre:
    def __init__(self, name):
        self.name = name
        self.movies = []

    def __repr__(self):
        return f"Genre('{self.name}', {len(self.movies)} films)"
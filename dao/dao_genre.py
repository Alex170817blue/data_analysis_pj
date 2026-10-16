class DaoGenre:
    def __init__(self):
        self._genres_map = {}

    def add_genre(self, genre):
        self._genres_map[genre.name] = genre

    def get_genre_by_name(self, name):
        return self._genres_map.get(name)

    def get_all_genres(self):
        return list(self._genres_map.values())
import json
import pickle

try:
    from imdb import IMDb
except ImportError:
    import os

    os.system("pip install imdbpy")
    from imdb import IMDb


class Movie:
    def __init__(self, name, year, category, country, producer, length, description, image):
        self.name = name
        self.year = year
        self.category = category
        self.country = country
        self.producer = producer
        self.length = length
        self.description = description
        self.image = image


class IMDBAPI:

    def __init__(self) -> None:
        self.films = list()
        self.app = IMDb()
        m = self.app.get_top250_movies()
        self.load_file()

    def initialise(self):
        print("Start fetching")
        self.films = list()
        self.load_file()

    def save_file(self):
        with open('film.pkl', 'wb') as output:
            pickle.dump(self.films, output, pickle.HIGHEST_PROTOCOL)

    def load_file(self):
        with open('film.pkl', 'rb') as input:
            self.films = pickle.load(input)

    def search_for_years(self, start_year, end_year):
        result = list()
        for i in self.films:
            if is_null(i):
                continue
            if start_year <= get_year(i) <= end_year:
                result.append(i)
        return result

    @staticmethod
    def search_for_country(country_category, films):
        result = list()
        if country_category == "Other":
            for i in films:
                if "Russia" not in get_country(i) and "United States" not in get_country(i):
                    result.append(i)
        else:
            for i in films:
                for j in get_country(i):
                    if j == country_category:
                        result.append(i)
        return result

    @staticmethod
    def search_for_genre(genre, films):
        result = list()
        for i in films:
            for j in get_genres(i):
                if j == genre:
                    result.append(i)
        return result

    """Return a movie or a list of movies as Movie objects"""
    def present_movie(self, start_year, end_year, country_category, genre):
        films = self.search_for_years(start_year, end_year)
        films = self.search_for_country(country_category, films)
        films = self.search_for_genre(genre, films)
        return create_film_list(films)


def get_image(film):
    return film.data["cover url"]


def get_year(film):
    return film.data["year"]


def is_null(film):
    for i in film.data.keys():
        if i == "year":
            return False
    return True


def get_country(film):
    return film.data["countries"]


def get_genres(film):
    return film.data["genres"]


def get_title(film):
    return film.data["title"]


def get_director(film):
    return film.data["director"][0].data["name"]


def get_length(film):
    return film.data["runtimes"][0]


def get_description(film):
    return film.data["plot"][0]


def create_film_list(films):
    result = list()
    for i in films:
        result.append(Movie(get_title(i), get_year(i), get_genres(i), get_country(i),
                            get_director(i), get_length(i), get_description(i), get_image(i)))
    return result

a = IMDBAPI()
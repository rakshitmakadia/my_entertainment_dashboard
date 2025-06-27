import tmdbsimple as tmdb
from tmdbsimple import Genres
import json
import constants
from datetime import datetime


def get_all_movie_genres():
    """
    Gets all movie genres from TMDb.

    Returns a list of dictionaries. Each genre is a dictionary with the keys "id" and "name".

    :return: A list of dictionaries
    """

    tmdb.API_KEY = constants.TMDB_API_KEY
    tmdb.REQUESTS_TIMEOUT = constants.TIMEOUT

    genres = Genres()
    res = genres.movie_list()
    return res["genres"]


def parse_from_url(url):
    """
    Given a URL, parse out the type (movie or tv) and ID.

    :param url: A string URL
    :return: A dictionary with keys "type" and "id"
    """
    return {
        "type": url.split("/")[-2].strip(),
        "id": int(url.split("/")[-1].split("-")[0].strip()),
    }


def get_movies_from_urls(url_file):
    """
    Given a file containing URLs, parse out all movie URLs and return a list of dictionaries containing the movie ID, type, and the source file name.

    :param url_file: The path to the file containing the URLs
    :return: A list of dictionaries with keys "id", "type", and "src_tag"
    """
    if not url_file:
        return None

    urls = []

    with open(url_file, "r") as f:
        urls = f.readlines()
    movie_ids = list(filter(lambda x: x["type"] == "movie", map(parse_from_url, urls)))

    for mov in movie_ids:
        mov["src_tag"] = url_file.split("\\")[-1]
    return movie_ids


def get_movie_details(movie_id):
    """
    Given a movie ID, fetches all relevant details from TMDb and returns them as a dictionary.

    :param movie_id: A string or integer representing the movie ID
    :return: A dictionary with keys "id", "imdb_id", "title", "original_title", "tagline", "overview", "runtime", "status", "release_date", "genres", "original_language", "spoken_languages", "origin_country", "popularity", "vote_average", "vote_count", "backdrop_path", "poster_path", and "belongs_to_collection"

    The returned dictionary keys are as follows:

    - "id": The TMDb ID of the movie
    - "imdb_id": The IMDB ID of the movie
    - "title": The title of the movie
    - "original_title": The original title of the movie
    - "tagline": The tagline of the movie
    - "overview": The overview of the movie
    - "runtime": The runtime of the movie in minutes
    - "status": The status of the movie (e.g. "Released")
    - "release_date": The release date of the movie
    - "genres": A JSON string containing the IDs of the movie's genres
    - "original_language": The original language of the movie
    - "spoken_languages": A JSON string containing the names of the languages spoken in the movie
    - "origin_country": A JSON string containing the origin country of the movie
    - "popularity": The popularity of the movie
    - "vote_average": The average vote of the movie
    - "vote_count": The number of votes the movie has received
    - "backdrop_path": The path to the movie's backdrop image
    - "poster_path": The path to the movie's poster image
    - "belongs_to_collection": The name and ID of the collection the movie belongs to (if it belongs to one)

    """
    tmdb.API_KEY = constants.TMDB_API_KEY
    tmdb.REQUESTS_TIMEOUT = constants.TIMEOUT

    movie = tmdb.Movies(movie_id)
    response = movie.info()

    movie_details = {
        "id": response["id"],
        "imdb_id": response["imdb_id"],
        "title": response["title"].replace("'", "`").replace('"', "`"),
        "original_title": response["original_title"]
        .replace("'", "`")
        .replace('"', "`"),
        "tagline": response["tagline"].replace("'", "`").replace('"', "`"),
        "overview": response["overview"].replace("'", "`").replace('"', "`"),
        "runtime": response["runtime"],
        "status": response["status"],
        "release_date": response["release_date"],
        "genres": json.dumps([genre["id"] for genre in response["genres"]]),
        "original_language": response["original_language"],
        "spoken_languages": json.dumps(
            [language["english_name"] for language in response["spoken_languages"]]
        ),
        "origin_country": json.dumps(response["origin_country"]),
        "popularity": response["popularity"],
        "vote_average": response["vote_average"],
        "vote_count": response["vote_count"],
        "backdrop_path": response["backdrop_path"],
        "poster_path": response["poster_path"],
        "belongs_to_collection": (
            response["belongs_to_collection"]["name"]
            .replace("'", "`")
            .replace('"', "`")
            + " ("
            + str(response["belongs_to_collection"]["id"])
            + ")"
            if response["belongs_to_collection"]
            else ""
        ),
    }

    return movie_details


def get_movie_library(movie_ids):
    """
    Given a list of dictionaries containing movie IDs and source file names, fetches all relevant details from TMDb and returns them as a list of dictionaries.

    :param movie_ids: A list of dictionaries with keys "id" and "src_tag"
    :return: A list of dictionaries with keys "id", "imdb_id", "title", "original_title", "tagline", "overview", "runtime", "status", "release_date", "genres", "original_language", "spoken_languages", "origin_country", "popularity", "vote_average", "vote_count", "backdrop_path", "poster_path", "belongs_to_collection", "src_tag", and "publication_id"

    """
    if not movie_ids:
        return None
    movie_library = []
    publication_id = int(datetime.now().strftime("%Y%m%d%H%M%S"))
    for mov in movie_ids:
        m_id = mov["id"]
        movie_details = get_movie_details(m_id)
        movie_details["src_tag"] = mov["src_tag"]
        movie_details["publication_id"] = publication_id
        movie_library.append(movie_details)

    return movie_library

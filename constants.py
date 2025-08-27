import os

TIMEOUT = 5
BASE_FILE_PATH = "tmp"


### FILEBASE
AWS_ACCESS_KEY_ID = os.getenv("FILEBASE_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("FILEBASE_SECRET")
BUCKET = os.getenv("FILEBASE_BUCKET")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")

### MYSQL AIVEN

HOST = os.getenv("AIVEN_DB_HOST")
PORT = int(os.getenv("AIVEN_DB_PORT"))
USER = os.getenv("AIVEN_DB_USER")
PASSWORD = os.getenv("AIVEN_DB_PASS")
DB = os.getenv("DB")
COLUMNS = [
    "id",
    "imdb_id",
    "title",
    "original_title",
    "tagline",
    "overview",
    "runtime",
    "status",
    "release_date",
    "genres",
    "original_language",
    "spoken_languages",
    "origin_country",
    "popularity",
    "vote_average",
    "vote_count",
    "backdrop_path",
    "poster_path",
    "belongs_to_collection",
    "src_tag",
    "publication_id",
]

### TMDB
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"
MOVIE_URL = "https://www.themoviedb.org/movie/movie_id"

### GOOGLE SHEETS
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
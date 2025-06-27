import mysqldb
import tmdb
import filebase


def main(write_files_to_buckets=True):
    """
    Executes the process of retrieving the latest movie URLs, extracting movie details from TMDb, and storing them in a MySQL database. It also handles the cleanup of outdated files and optional upload of files to an S3 bucket.

    The function performs the following steps:
    1. Connects to the MySQL database.
    2. Retrieves the latest URL file from the S3 bucket.
    3. Parses the URLs to extract movie IDs.
    4. Fetches movie details from TMDb using the extracted movie IDs.
    5. Inserts the movie details into the 'movie_details' table in the database.
    6. Reads and writes the contents of the 'movie_details' table to an Excel file.
    7. Deletes files in the S3 bucket that are older than 30 days.
    8. Optionally uploads files from local storage to the S3 bucket.
    9. Cleans up local temporary files.

    :param write_files_to_buckets: A boolean indicating whether to upload files to the S3 bucket.
    :return: None
    """

    filebase.create_local_tmp()
    conn = mysqldb.get_mysql_conn()
    url_file = filebase.get_latest_url_file()
    movie_ids = tmdb.get_movies_from_urls(url_file)
    movie_library = tmdb.get_movie_library(movie_ids)
    insert_status = mysqldb.insert_into_movie_details(
        conn, movie_library, leave_open=True
    )

    print("Insert status: ", insert_status)

    print("Reading 'movie_details' table...")

    select_movie_details_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql", "select_from_movie_details.sql")
    result = mysqldb.select_from_table(
        conn, select_movie_details_path, write_to_file=True
    )
    # print(result)

    filebase.delete_folder_30days()

    if write_files_to_buckets:
        filebase.upload_to_folder()

    filebase.local_tmp_cleanup()


if __name__ == "__main__":
    main()

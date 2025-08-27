import mysqldb
import tmdb
import filebase
import os


def main(write_files_to_buckets=True):
    """
    Main function to orchestrate the process of updating and managing movie details.
    This function performs the following steps:
    1. Creates a local temporary directory for file operations.
    2. Establishes a connection to the MySQL database.
    3. Retrieves the latest URL file containing movie data.
    4. Extracts movie IDs from the URL file.
    5. Fetches detailed movie information for the extracted IDs.
    6. Inserts or updates the movie details in the database.
    7. Reads the 'movie_details' table using a custom SQL query and writes the results to a file and Google Sheet.
    8. Deletes temporary folders older than 30 days.
    9. Optionally uploads files to a remote storage bucket.
    10. Cleans up the local temporary directory.
    Args:
        write_files_to_buckets (bool, optional): If True, uploads generated files to a remote storage bucket. Defaults to True.
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
        conn, select_movie_details_path, write_to_file=True, write_to_gsheet=True
    )
    
    filebase.delete_folder_30days()

    if write_files_to_buckets:
        filebase.upload_to_folder()

    filebase.local_tmp_cleanup()


if __name__ == "__main__":
    main()

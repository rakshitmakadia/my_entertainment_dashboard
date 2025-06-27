import filebase
import mysqldb
import tmdb


def main(write_files_to_buckets=True):
    """
    Connects to the MySQL database, fetches all movie genres from TMDb, and creates a table called 'genres' if it doesn't exist. If the table does exist, it will be dropped and recreated.

    The function takes in a boolean indicating whether to write the files to the buckets.

    If write_files_to_buckets is True, the function will upload the files to the buckets.

    The function will then delete all objects in the specified S3 bucket that are older than 30 days, and delete all local files in the directory specified in constants.BASE_FILE_PATH and its subdirectories.

    :param write_files_to_buckets: A boolean indicating whether to write the files to the buckets
    :return: None
    """
    filebase.create_local_tmp()
    conn = mysqldb.get_mysql_conn()
    data = tmdb.get_all_movie_genres()
    genre_table_data = mysqldb.generate_genres_table(conn, data)
    # print(genre_table_data)
    if write_files_to_buckets:
        filebase.upload_to_folder()

    filebase.delete_folder_30days()
    filebase.local_tmp_cleanup()


if __name__ == "__main__":
    main()

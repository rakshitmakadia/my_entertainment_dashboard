import constants
import os
import codecs
import pymysql


def get_mysql_conn():
    # conn_str = f"mysql://{user}:{password}@{host}:{port}/{db}"

    """
    Connects to the MySQL database using the constants from the constants module.

    The constants module should contain the following variables:
        - HOST
        - PORT
        - USER
        - PASSWORD
        - DB
        - TIMEOUT

    Returns a pymysql connection object.

    :return: A pymysql connection object
    """
    conn = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=constants.TIMEOUT,
        cursorclass=pymysql.cursors.DictCursor,
        db=constants.DB,
        host=constants.HOST,
        password=constants.PASSWORD,
        read_timeout=constants.TIMEOUT,
        port=constants.PORT,
        user=constants.USER,
        write_timeout=constants.TIMEOUT,
    )

    return conn


def generate_genres_table(conn, data, leave_open=False):
    """
    Connects to the MySQL database using the provided connection object, and creates a table called 'genres' with two columns - 'id' and 'name'.

    The function takes in a connection object, a list of dictionaries containing the data to be inserted into the 'genres' table, and a boolean indicating whether to leave the connection open.

    If the leave_open parameter is False, the connection will be closed when the function is finished.

    The function will return the result of the select statement as a list of dictionaries, each dictionary containing the column names and their associated values.

    If the table doesn't exist, the function will create the table and insert the data from the list of dictionaries.

    If the table exists, the function will drop the table and create it again with the new data.

    :param conn: A pymysql connection object
    :param data: A list of dictionaries containing the data to be inserted into the 'genres' table
    :param leave_open: A boolean indicating whether to leave the connection open
    :return: A list of dictionaries, each dictionary containing the column names and their associated values
    """
    result = None
    genre_drop = "DROP TABLE genres"
    genre_create = "CREATE TABLE genres (id INTEGER PRIMARY KEY, name VARCHAR(32))"
    genre_insert = dict_list_to_insert_str(data, "genres", ["id", "name"])
    genre_read = None
    genre_select_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql", "select_from_genres.sql")
    with open(genre_select_path, "r") as f:
        genre_read = f.read()

    try:
        cursor = conn.cursor()
        print("Dropping 'genres' table...")
        cursor.execute(genre_drop)
    except Exception as e:
        print(e)
        print("Table doesn't exist, creating...")

    try:
        cursor = conn.cursor()
        cursor.execute(genre_create)
        print("Table 'genres' created...")
        cursor.execute(genre_insert)
        print("Table 'genres' populated...")
        print("Reading 'genres' table...")
        cursor.execute(genre_read)
        result = cursor.fetchall()
    finally:
        conn.commit()
        if not leave_open:
            print("Closing connection...")
            conn.close()
            print("Connection closed...")

    return result


def create_or_replace_movie_details_table(conn, leave_open=False):
    """
    Connects to the MySQL database using the provided connection object, and creates a table named "movie_details" if it doesn't exist. If the table does exist, it will be dropped and recreated.

    The table will have the following columns:
        - id (integer)
        - imdb_id (string)
        - title (string)
        - original_title (string)
        - tagline (string)
        - overview (string)
        - runtime (integer)
        - status (string)
        - release_date (string)
        - genres (JSON string)
        - original_language (string)
        - spoken_languages (JSON string)
        - origin_country (JSON string)
        - popularity (decimal)
        - vote_average (decimal)
        - vote_count (integer)
        - backdrop_path (string)
        - poster_path (string)
        - belongs_to_collection (string)
        - src_tag (string)
        - publication_id (integer)

    The function will return nothing.

    If leave_open is False, the connection will be closed when the function is finished.

    :param conn: A pymysql connection object
    :param leave_open: A boolean indicating whether to leave the connection open
    """
    try:
        cursor = conn.cursor()
        print("Dropping table...")
        cursor.execute("DROP TABLE movie_details")
    except Exception as e:
        print(e)
        print("Table doesn't exist. Proceeding to create the table...")

    try:
        cursor = conn.cursor()
        ddl = ""
        create_movie_details_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql", "create_table_movie_details.sql")
        with open(create_movie_details_path, "r") as f:
            ddl = f.read()
        cursor.execute(ddl)
        print("Table 'movie_details' created...")
    finally:
        conn.commit()
        if not leave_open:
            print("Closing connection...")
            conn.close()
            print("Connection closed...")


def select_from_table(conn, select_query, leave_open=False, write_to_file=False):
    """
    Connects to the MySQL database using the provided connection object, and executes a select statement defined in a file.

    The function takes in a connection object, a file path to a SQL select statement, a boolean indicating whether to leave the connection open, and a boolean indicating whether to write the result to an Excel file.

    If the leave_open parameter is False, the connection will be closed when the function is finished.

    If the write_to_file parameter is True, the function will write the result to an Excel file in the directory specified in constants.BASE_FILE_PATH.

    The function will return the result of the select statement as a list of dictionaries, each dictionary containing the column names and their associated values.

    If the select statement fails to execute, an error message will be printed with details of the error.

    If the write_to_file parameter is True and the file fails to write, an error message will be printed with details of the error.

    :param conn: A pymysql connection object
    :param select_query: A file path to a SQL select statement
    :param leave_open: A boolean indicating whether to leave the connection open
    :param write_to_file: A boolean indicating whether to write the result to an Excel file
    :return: A list of dictionaries, each dictionary containing the column names and their associated values
    """
    result = None
    select_sql = None
    with open(select_query, "r") as f:
        select_sql = f.read()

    try:
        cursor = conn.cursor()
        cursor.execute(select_sql)
        result = cursor.fetchall()
        if write_to_file:
            import pandas as pd

            df = pd.DataFrame(result)
            xlsx_name = (
                select_query.split(".")[0].split("\\")[-1].split("/")[-1] + ".xlsx"
            )
            xlsx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), constants.BASE_FILE_PATH, xlsx_name)
            df.to_excel(xlsx_path, index=False)
        print("Got results from the select statement...")

    finally:
        if not leave_open:
            print("Closing connection...")
            conn.close()
            print("Connection closed...")

    return result


def insert_into_movie_details(conn, movie_library, leave_open=False):
    """
    Inserts a list of movie dictionaries into the 'movie_details' table of a MySQL database using the provided connection object.

    The function takes in a connection object, a list of dictionaries containing the movie details, and a boolean indicating whether to leave the connection open.

    If the leave_open parameter is False, the connection will be closed when the function is finished.

    The function will return a string indicating whether the insert statement was successful or not.

    If the insert statement fails to execute, an error message will be printed with details of the error.

    :param conn: A pymysql connection object
    :param movie_library: A list of dictionaries containing the movie details
    :param leave_open: A boolean indicating whether to leave the connection open
    :return: A string indicating whether the insert statement was successful or not
    """
    create_or_replace_movie_details_table(conn, leave_open=True)
    
    if not movie_library:
        if not leave_open:
            print("Closing connection...")
            conn.close()
            print("Connection closed...")
        return "Nothing to insert..."

    table_name = "movie_details"
    print("Generating insert statement...")
    insert_sql = dict_list_to_insert_str(movie_library, table_name, constants.COLUMNS)

    response = "Failed"

    try:
        cursor = conn.cursor()
        print("Executing insert statement...")
        cursor.execute(insert_sql)
        result = cursor.fetchall()
        response = "Success\n" + str(result)
    except Exception as e:
        print(e)

    finally:
        conn.commit()
        if not leave_open:
            print("Closing connection...")
            conn.close()
            print("Connection closed...")

    return response


def dict_list_to_insert_str(data, table, cols):
    """
    Takes in a list of dictionaries, a table name, and a list of column names, and returns a string representing an SQL insert statement for the given table.

    The function also writes the insert statement to a file in the directory specified in constants.BASE_FILE_PATH.

    :param data: A list of dictionaries containing the data to be inserted into the table
    :param table: A string representing the table name
    :param cols: A list of strings representing the column names
    :return: A string representing the insert statement
    """
    cols_str = ", ".join(cols)
    insert_str = f"INSERT INTO {table} ({cols_str}) VALUES "
    vals_str = ""
    for val in data:
        vals_str = vals_str + "("
        for col in cols:
            try:
                vals_str = vals_str + "'" + val[col] + "', "
            except TypeError as e:
                vals_str = vals_str + str(val[col]) + ", "
        vals_str = vals_str[:-2] + "), "
    vals_str = vals_str[:-2]
    insert_str = insert_str + vals_str
    insert_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), constants.BASE_FILE_PATH, f"insert_into_{table}.sql"
    )
    with codecs.open(insert_file_path, "w", "utf-8") as f:
        f.write(insert_str)
        print(
            f"Insert statement written to file: {os.path.join(constants.BASE_FILE_PATH, f'insert_into_{table}.sql')}"
        )

    return insert_str

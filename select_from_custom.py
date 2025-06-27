import mysqldb
import sys
import filebase

def main():
    """
    Connects to the MySQL database using the connection object returned by mysqldb.get_mysql_conn(), and executes a select statement defined in a file.

    The function takes in a file path to a SQL select statement as a command line argument.

    If the select statement fails to execute, an error message will be printed with details of the error.

    If the write_to_file parameter is True and the file fails to write, an error message will be printed with details of the error.

    The function will return nothing.

    :return: None
    """
    sql_file = sys.argv[1]
    conn = mysqldb.get_mysql_conn()
    result = mysqldb.select_from_table(conn, sql_file, write_to_file=True)
    # print(result)
    print(
        "Result written to file "
        + sql_file.split(".")[0].split("\\")[-1].split("/")[-1]
        + ".xlsx"
    )

    print("Uploading the file to filebase bucket...")
    filebase.upload_to_folder()


    mysqldb.local_tmp_cleanup()


if __name__ == "__main__":
    main()

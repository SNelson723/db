import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        dbname="mydb",
        user="postgres",
        password="Maiden00931!1",
        host="localhost",
        port="5432"
    )
    try:
        yield conn
    finally:
        conn.close()
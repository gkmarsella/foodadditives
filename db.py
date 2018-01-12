import psycopg2
import psycopg2.extras

def connect():
    c = psycopg2.connect("dbname=additive-db")
    return c


def additive_database(name, description, uses, toxicity):
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM additive_db")
    additive_db = cur.fetchall()
    cur.close()
    conn.close()
    return additive_db
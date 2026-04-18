import psycopg2
import os

def run_job():
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()

        cur.execute("INSERT INTO spiele_web (created_at) VALUES (NOW())")

        conn.commit()
        cur.close()
        conn.close()

        return "OK"

    except Exception as e:
        print("Fehler:", e)
        return "ERROR"


if __name__ == "__main__":
    run_job()
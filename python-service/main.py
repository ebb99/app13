from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

@app.get("/run-job")
def run_job():
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()

        cur.execute("INSERT INTO spiele_web (created_at) VALUES (NOW())")

        conn.commit()
        cur.close()
        conn.close()

        return {"status": "ok"}

    except Exception as e:
        return {"error": str(e)}
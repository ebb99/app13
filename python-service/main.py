from fastapi import FastAPI
import psycopg2
from psycopg2 import pool
import os

app = FastAPI()

db_pool = None

@app.on_event("startup")
def startup():
    global db_pool
    db_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        dsn=os.environ["DATABASE_URL"],
        sslmode="require"
    )

@app.on_event("shutdown")
def shutdown():
    global db_pool
    if db_pool:
        db_pool.closeall()

@app.post("/run-job")
def run_job():
    conn = None
    try:
        conn = db_pool.getconn()
        cur = conn.cursor()

        cur.execute("INSERT INTO spiele_web (created_at) VALUES (NOW())")
        conn.commit()

        cur.close()

        return {"status": "ok"}

    except Exception as e:
        if conn:
            conn.rollback()
        print("FEHLER:", e)
        return {"status": "error", "message": str(e)}

    finally:
        if conn:
            db_pool.putconn(conn)
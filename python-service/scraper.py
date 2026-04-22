import os
import psycopg2

async def run_scraper(job_id=None, jobs=None):
    print("🚀 Scraper gestartet")

    db_url = os.environ.get("DATABASE_URL")
    print("DB URL:", db_url)

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("SELECT NOW();")
    print("DB OK:", cur.fetchone())

    conn.close()
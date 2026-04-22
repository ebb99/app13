import os
import psycopg2

def run_scraper(job_id=None, jobs=None):
    try:
        print("🚀 Scraper gestartet")

        db_url = os.environ.get("DATABASE_URL")
        print("DB URL:", db_url)

        conn = psycopg2.connect(db_url, sslmode="require")
        cur = conn.cursor()

        cur.execute("SELECT 1;")
        print("DB OK:", cur.fetchone())

        conn.close()

    except Exception as e:
        print("❌ DB ERROR:", e)
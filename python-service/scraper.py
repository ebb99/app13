import os
import psycopg2

def run_scraper(job_id=None, jobs=None):
    try:
        print("🚀 Scraper gestartet")

        db_url = os.environ.get("DATABASE_URL")
        print("DB URL:", db_url)

        if not db_url:
            raise Exception("❌ DATABASE_URL ist nicht gesetzt!")

        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        cur.execute("SELECT NOW();")
        print("DB OK:", cur.fetchone())

        conn.close()

    except Exception as e:
        print("❌ SCRAPER ERROR:", e)
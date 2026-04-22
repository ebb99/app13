from fastapi import FastAPI,BackgroundTasks
import asyncpg
import os
from scraper import run_scraper

app = FastAPI()

db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        min_size=1,
        max_size=5,
        ssl="require"
    )

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

@app.post("/run-job")
async def run_job(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(run_scraper)
        return {
            "status": "ok",
            "message": "Scraper wurde gestartet"
        }

    except Exception as e:
        print("FEHLER:", e)
        return {"status": "error", "message": str(e)}
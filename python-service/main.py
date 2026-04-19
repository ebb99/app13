from fastapi import FastAPI
import asyncpg
import os

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
async def run_job():
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO spiele_web (created_at) VALUES (NOW())"
            )

        return {"status": "ok"}

    except Exception as e:
        print("FEHLER:", e)
        return {"status": "error", "message": str(e)}
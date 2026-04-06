import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import scheduler
from api.routes import router
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background polling on app startup
    task = asyncio.create_task(scheduler.poll_loop())
    yield
    # Shutdown: cancel the polling task cleanly
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Bar & Bench Scraper",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI
from app.core.config import setting
from app.routes.user_routes import user_router
import os
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.redis import init_redis_pool, redis_close

@asynccontextmanager
async def redis_life_cycle(app: FastAPI):
    await init_redis_pool()
    yield
    await redis_close()

os.makedirs(setting.AVAITAR_S,exist_ok=True)

app = FastAPI(
    version=setting.APP_VERSION,
    title=setting.APP_TITLE,
    lifespan=redis_life_cycle
)

app.include_router(router=user_router)

app.mount(f"/{setting.UPLOAD_DIR}",StaticFiles(directory=f"{setting.UPLOAD_DIR}"),name=f"{setting.UPLOAD_DIR}")

@app.get('/')
async def home():
    return {"Message":"That is a Task Management System"}
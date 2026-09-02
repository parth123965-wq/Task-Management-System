from fastapi import FastAPI, Request
from app.core.config import setting
from app.routes.user_routes import user_router
import os
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.redis import init_redis_pool, redis_close
import redis
from fastapi.responses import JSONResponse
from app.core.email import EmailManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_pool()
    await EmailManager.initilization_email_service()
    yield
    await redis_close()
    await EmailManager.shutdown_email_service()

os.makedirs(setting.AVAITAR_S,exist_ok=True)

app = FastAPI(
    version=setting.APP_VERSION,
    title=setting.APP_TITLE,
    lifespan=lifespan
)

@app.exception_handler(redis.exceptions.ConnectionError)
async def redis_error_handler(request: Request, exc: redis.exceptions.ConnectionError):
    return JSONResponse(status_code=503, content={"detail": "Database/Redis service is offline"})

app.include_router(router=user_router)

app.mount(f"/{setting.UPLOAD_DIR}",StaticFiles(directory=f"{setting.UPLOAD_DIR}"),name=f"{setting.UPLOAD_DIR}")

@app.get('/')
async def home():
    return {"Message":"That is a Task Management System"}
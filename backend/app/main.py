from fastapi import FastAPI
from app.core.config import setting
from app.routes.user_routes import user_router
import os
from fastapi.staticfiles import StaticFiles

os.makedirs(setting.AVAITAR_S,exist_ok=True)

app = FastAPI(
    version=setting.APP_VERSION,
    title=setting.APP_TITLE
)

app.include_router(router=user_router)

app.mount(f"/{setting.UPLOAD_DIR}",StaticFiles(directory=f"{setting.UPLOAD_DIR}"),name=f"{setting.UPLOAD_DIR}")

@app.get('/')
async def home():
    return {"Message":"That is a Task Management System"}
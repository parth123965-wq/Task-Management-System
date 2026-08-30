from fastapi import FastAPI
from app.core.config import setting
from app.routes.user_routes import user_router

app = FastAPI(
    version=setting.APP_VERSION,
    title=setting.APP_TITLE
)

app.include_router(router=user_router)

@app.get('/')
async def home():
    return {"Message":"That is a Task Management System"}
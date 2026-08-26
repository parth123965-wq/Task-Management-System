from fastapi import FastAPI
from app.core.config import setting

app = FastAPI(
    version=setting.APP_VERSION,
    title=setting.APP_TITLE
)

@app.get('/')
async def home():
    return {"Message":"That is a Task Management System"}
from fastapi import FastAPI, Request, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db, get_db, User
from auth import get_user_from_token
from routers import auth_router, courses_router, consult_router
import os

app = FastAPI(title="Zed Consult")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth_router.router)
app.include_router(courses_router.router)
app.include_router(consult_router.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("static/index.html")
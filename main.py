from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from routers.auth_router import router as auth_router
from routers.courses_router import router as courses_router
from routers.consult_router import router as consult_router

app = FastAPI(title="Zed Consult")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(consult_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("static/index.html")
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.notes import router as notes_router
from api.security import login, logout, require_auth
from config import APP_CONFIG
import storage

app = FastAPI(title="Server Notes", version="1.0.0")

static_dir = Path(__file__).parent / "web" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_data_dir():
    storage.ensure_dirs()


@app.get("/")
def serve_index():
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="缺少前端文件")
    return FileResponse(index_path)


@app.post("/api/login")
def login_endpoint(request: Request, password: str = Form("")):
    return login(password, request)


@app.post("/api/logout")
def logout_endpoint(deps: bool = Depends(require_auth)):
    return logout()


@app.get("/api/config")
def config_info():
    return {"auth_enabled": bool(APP_CONFIG.get("ADMIN_PASSWORD"))}


app.include_router(notes_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=APP_CONFIG["HOST"], port=APP_CONFIG["PORT"])

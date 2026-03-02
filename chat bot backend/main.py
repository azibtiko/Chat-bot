import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app_chatbot.chatbot import router as chatbot_router

from web import Context

app = FastAPI(debug=True)

ALLOWED_ORIGINS = [
    "null",
    "http://localhost:3060",
    "http://127.0.0.1:3060",
    "http://localhost:3061",
    "http://127.0.0.1:3061",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
]

# Allow any localhost/lan origin (Expo web / device tunnels) without enumerating every port.
LOCAL_ORIGIN_REGEX = (
    r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?$"
)

allow_all = os.getenv("EDUCARE_ALLOW_ALL_ORIGINS", "false").lower() in {
    "1",
    "true",
    "yes",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else ALLOWED_ORIGINS,
    allow_origin_regex=None if allow_all else LOCAL_ORIGIN_REGEX,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],  # requires Authorization for user token fetches
)


app.add_middleware(Context)

app.include_router(chatbot_router)


@app.middleware("http")
async def log_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:  # pragma: no cover - Diagnostics middleware
        raise


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

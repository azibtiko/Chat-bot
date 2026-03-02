from typing import Optional
import os
from dotenv import load_dotenv

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from sqlalchemy import create_engine

load_dotenv(override=True)


# Global SQLAlchemy engine
def _db_url() -> str:
    env_url = os.getenv("CHATBOT_DATABASE_URL")
    if env_url:
        return env_url

    user = os.getenv("CHATBOT_DB_USER")
    password = os.getenv("CHATBOT_DB_PASSWORD")
    host = os.getenv("CHATBOT_DB_HOST", "localhost")
    name = os.getenv("CHATBOT_DB_NAME")
    if user and password and name:
        return f"mysql+pymysql://{user}:{password}@{host}/{name}"

    raise RuntimeError(
        "Database credentials are missing. Set CHATBOT_DATABASE_URL or "
        "CHATBOT_DB_USER/CHATBOT_DB_PASSWORD/CHATBOT_DB_NAME."
    )


# Global SQLAlchemy engine
engine = create_engine(_db_url())


class RequestContext:
    def __init__(self, request: Optional[Request] = None, connection=None):
        self.request = request
        self.conn = connection
        self._init_from_request()

    def _init_from_request(self):
        if self.request:
            self.x_api_key = self.request.headers.get("x-api-key")
        if self.conn is None:
            self.conn = engine.connect()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


class Context(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        connection = engine.connect()
        request_context = RequestContext(request=request, connection=connection)
        request.state.context = request_context
        request.state.db = connection
        try:
            response = await call_next(request)
        finally:
            request_context.close()
            request.state.context = None
            request.state.db = None
        return response


def get_context(request: Request) -> RequestContext:
    context = getattr(request.state, "context", None)
    if context is None:
        raise RuntimeError("Context middleware must be installed")
    return context

def get_context_with_user_info(request: Request) -> tuple[object]:
    context = get_context(request)
    return context

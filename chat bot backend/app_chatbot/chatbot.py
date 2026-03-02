from fastapi import FastAPI, APIRouter, Request, HTTPException, status, Query
from typing import Optional
from lib_chatbot.models.chatbot import CreateChatRequest, ChatResponse, CreateTraceRequest, TraceModel, AnalyticsResponse
from lib_chatbot.chatbot import get_bot_response, get_trace_response, get_trace_data, get_analytics_data
from web import get_context_with_user_info


router = APIRouter()


@router.post("/chat")
async def chat(request: Request, payload: CreateChatRequest) -> ChatResponse:
    context = get_context_with_user_info(request)
    bot_response, response_time = await get_bot_response(conn=context.conn, payload=payload)

    return ChatResponse(bot_response=bot_response, response_time_ms=response_time)


@router.post("/traces")
async def traces(request: Request, payload: CreateTraceRequest) -> TraceModel:
    context = get_context_with_user_info(request)
    trace = await get_trace_response(conn=context.conn, payload=payload)

    return trace


@router.get("/traces")
def traces(request: Request, category: Optional[list[str]] = Query(None)) -> list[TraceModel]:
    context = get_context_with_user_info(request)
    return get_trace_data(conn=context.conn, category=category)


@router.get("/analytics")
def analytics(request: Request) -> AnalyticsResponse:
    context = get_context_with_user_info(request)
    return get_analytics_data(conn=context.conn)

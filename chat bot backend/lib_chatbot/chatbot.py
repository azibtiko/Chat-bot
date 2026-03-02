from unicodedata import category
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from lib_utils.sql import sql
from lib_chatbot.models.chatbot import CreateChatRequest, CreateTraceRequest, TraceModel, AnalyticsResponse, AnalyticsCategoryStats
from lib_utils.llm_support import generate_chatbot_response, classify_conversation
from lib_utils.unique_code import generate_unique_code

async def get_bot_response(conn, payload: CreateChatRequest) -> str:
    bot_response, response_time = await generate_chatbot_response(payload.user_message)
    return bot_response, response_time


async def get_trace_response(conn, payload: CreateTraceRequest) -> TraceModel:
    category = await classify_conversation(payload.user_message, payload.bot_response)
    trace_code = generate_unique_code("TRC")
    try:
        sql(conn).insert_one(
            "trace",
            {
                "trace_code": trace_code,
                "user_message": payload.user_message,
                "bot_response": payload.bot_response,
                "category": category,
                "response_time_ms": payload.response_time_ms 
            }
        )
        conn.commit()
    except SQLAlchemyError as exc:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Data base error occurred"
        )
    
    trace = sql(
        conn,
        """
        select * from trace where trace_code = :trace_code
        """,
        {
            "trace_code": trace_code
        }
    ).dict()

    return TraceModel(**trace)


def get_trace_data(conn, category) -> list[TraceModel]:
    base_query = "SELECT * FROM trace"
    params = {}

    if category:
        placeholders = ", ".join(f":cat{i}" for i in range(len(category)))
        base_query += f" WHERE category IN ({placeholders})"
        for i, cat in enumerate(category):
            params[f"cat{i}"] = cat
    
    base_query += " ORDER BY created_at DESC"
    
    try:
        traces = sql(conn,
            base_query,
            params
        ).dicts()
    except SQLAlchemyError as exc:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Data base error occurred"
        )
    
    return [TraceModel(**trace) for trace in traces]


def get_analytics_data(conn) -> AnalyticsResponse:
    try:
        result = sql(
            conn,
            """
            SELECT
                COUNT(*) AS total_traces,
                AVG(response_time_ms) AS average_response_time_ms
            FROM trace;
            """
            ,
        ).dict()
        total_traces, average_response_time_ms = result["total_traces"], result["average_response_time_ms"]

        analytics_data = sql(
            conn,
            """
            SELECT
                category,
                COUNT(*) AS category_count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trace) AS percentage
            FROM trace
            GROUP BY category;

            """,
        ).dicts()
    except SQLAlchemyError as exc:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Data base error occurred"
        )
    

    by_category = {
        a["category"]: AnalyticsCategoryStats(
            count=a["category_count"],
            percentage=float(a["percentage"])
        )
        for a in analytics_data
    }
    return AnalyticsResponse(
        total_traces=total_traces,
        average_response_time_ms=int(average_response_time_ms),
        by_category=by_category
    )

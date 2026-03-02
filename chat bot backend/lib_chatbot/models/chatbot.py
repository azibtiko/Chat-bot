from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Dict


class CreateChatRequest(BaseModel):
    user_message: str


class ChatResponse(BaseModel):
    bot_response: str
    response_time_ms: int


class CreateTraceRequest(BaseModel):
    user_message: str
    bot_response: str
    response_time_ms: int


class TraceCategory(str, Enum):
    Billing="Billing"
    Refund="Refund"
    Account_Access="Account_Access"
    Cancellation="Cancellation"
    General_inquiry="General_Inquiry"


class TraceModel(BaseModel):
    id: int
    trace_code: str
    user_message: str
    bot_response: str
    category: str
    response_time_ms: int
    created_at: datetime    


class AnalyticsCategoryStats(BaseModel):
    count: int
    percentage: float


class AnalyticsResponse(BaseModel):
    total_traces: int
    average_response_time_ms: int
    by_category: Dict[str, AnalyticsCategoryStats]


import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ..schemas.chat import ChatRequest, ChatResponse
from ...agents.manager_agent import ManagerAgent

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")  # type: ignore[misc]
async def health_check() -> Any:
    """Health check endpoint"""
    return {"status" : "ok"}



@router.post("/", response_model=ChatResponse)  # type: ignore[misc]
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        agent: ManagerAgent = ManagerAgent.get_agent()
        result = await agent.handle_message(request.message)
        return ChatResponse(message=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



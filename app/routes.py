from fastapi import APIRouter, HTTPException

from agent import agent
from models import ChatRequest, ChatResponse


router = APIRouter()


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    try:

        result = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        })

        messages = result.get(
            "messages",
            []
        )

        if not messages:
            return ChatResponse(
                response="The agent returned no response."
            )

        last_message = messages[-1]

        response_text = getattr(
            last_message,
            "content",
            ""
        )

        if isinstance(
            response_text,
            list
        ):

            response_text = "\n".join(
                str(item)
                for item in response_text
            )

        return ChatResponse(
            response=str(
                response_text
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
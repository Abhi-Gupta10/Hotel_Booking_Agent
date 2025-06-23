from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from booking_graph import agent_executor  # This should be your LangGraph agent
from db import init_db
from typing import Dict, Any

app = FastAPI()
init_db()

class WebhookMessage(BaseModel):
    username: str
    message: str

VERIFY_TOKEN = "2yuSvkBST0kjLEaB3zFqNQ9L0GW_5YaQxUuoadibH1vooEYsu"

# Webhook Verification (GET)
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

# Webhook Handler (POST)
@app.post("/webhook")
async def handle_webhook(input_data: WebhookMessage):
    """
    Handle incoming webhook with username and message
    Example request body:
    {
        "username": "john_doe",
        "message": "Hello world"
    }
    """
    try:
        print(f"Received message from {input_data.username}: {input_data.message}")
        
        # Prepare the input state for the LangGraph agent
        initial_state = {
            "messages": [{"role": "user", "content": input_data.message}],
            "user_id": input_data.username,
            "current_booking": None,
            "booking_in_progress": False,
            "rescheduling": False
        }
        
        # Invoke the LangGraph agent
        result = agent_executor.invoke(initial_state)
        
        # Get the last assistant message
        last_message = result["messages"][-1]["content"]
        
        return JSONResponse({
            "status": "success",
            "username": input_data.username,
            "response": last_message
        })
    
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
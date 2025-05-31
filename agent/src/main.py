# from agents import Agent, Runner

# agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
# print(result.final_output)

from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from agents import Agent, Runner

# Load environment variables
load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

agent = Agent(name="Assistant", instructions="You are a receptionist that helps the user schedule an appointment with a doctor.", model="gpt-4o-mini")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="MedApp Agent",
    description="Agent for medical application",
    version="0.1.0",
    lifespan=lifespan
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        while True:
                prompt = await websocket.receive_text()
                result = await Runner.run(agent, prompt)
                await websocket.send_text(f"Message text was: {result.final_output}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=HOST,
        port=PORT
    )



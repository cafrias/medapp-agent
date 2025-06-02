# from agents import Agent, Runner

# agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
# print(result.final_output)

from contextlib import asynccontextmanager
from datetime import datetime
import os
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from agents import Agent, Runner, function_tool
from agents.mcp.server import MCPServerSse, MCPServerSseParams

# Load environment variables
load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
SCHEDULER_URL = os.getenv("SCHEDULER_URL", "http://localhost:8000/mcp")

@function_tool
def get_current_time():
    """
    Get the current time in ISO format
    """
    return datetime.now().isoformat()

# Read instructions from file
instructions = ""
with open("src/instructions.md", "r") as f:
    instructions = f.read()

scheduler_mcp = MCPServerSse(
    params=MCPServerSseParams(
         url=SCHEDULER_URL
    ),
    name="Scheduler MCP",
)

agent = Agent(name="Assistant", instructions=instructions, model="gpt-4o-mini", mcp_servers=[scheduler_mcp], tools=[get_current_time])

@asynccontextmanager
async def lifespan(app: FastAPI):
    await scheduler_mcp.connect()
    yield
    await scheduler_mcp.cleanup()

app = FastAPI(
    title="MedApp Agent",
    description="Agent for medical application",
    version="0.1.0",
    lifespan=lifespan
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        input_list = []

        while True:
            prompt = await websocket.receive_text()
            input_list.append({ "role": "user", "content": prompt })
            result = await Runner.run(agent, input_list)
            input_list = result.to_input_list()
            await websocket.send_text(result.final_output)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=HOST,
        port=PORT
    )



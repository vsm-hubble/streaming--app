import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import Part, Content
from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response

from finagent.agent import root_agent

# Load environment variables
load_dotenv()

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Application configuration
APP_NAME = "financial_streaming_app"
session_service = InMemorySessionService()

# Initialize FastAPI app
app = FastAPI()

# Serve static files - use absolute path
STATIC_DIR = BASE_DIR / "static"

# Ensure static directory exists
if not STATIC_DIR.exists():
    print(f"WARNING: Static directory not found at {STATIC_DIR}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Base directory: {BASE_DIR}")
else:
    print(f"Static directory found at: {STATIC_DIR}")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


async def start_agent_session(user_id: str, is_audio: bool = False):
    """
    Starts an ADK agent session for the given user.
    
    Args:
        user_id (str): Unique identifier for the user
        is_audio (bool): Whether to use audio mode (False for text-only)
    
    Returns:
        tuple: (live_events, live_request_queue)
    """
    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )
    
    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )
    
    # Set response modality (TEXT only for this implementation)
    modality = "TEXT"  # Always TEXT for this financial app
    run_config = RunConfig(response_modalities=[modality])
    
    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()
    
    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket: WebSocket, live_events):
    """
    Streams agent responses to the WebSocket client.
    
    Args:
        websocket (WebSocket): The WebSocket connection
        live_events: Async iterator of agent events
    """
    try:
        async for event in live_events:
            # Handle turn completion or interruption
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: {message}")
                continue
            
            # Read the Content and its first Part
            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part:
                continue
            
            # Handle text content (no audio in this implementation)
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {part.text[:50]}...")
                
    except Exception as e:
        print(f"Error in agent_to_client_messaging: {e}")
        raise


async def client_to_agent_messaging(websocket: WebSocket, live_request_queue: LiveRequestQueue):
    """
    Relays client messages to the ADK agent.
    
    Args:
        websocket (WebSocket): The WebSocket connection
        live_request_queue (LiveRequestQueue): Queue to send messages to the agent
    """
    try:
        while True:
            # Receive and decode JSON message from client
            message_json = await websocket.receive_text()
            message = json.loads(message_json)
            
            mime_type = message.get("mime_type")
            data = message.get("data")
            
            # Handle text messages only
            if mime_type == "text/plain":
                # Send text message to the agent
                content = Content(role="user", parts=[Part.from_text(text=data)])
                live_request_queue.send_content(content=content)
                print(f"[CLIENT TO AGENT]: {data}")
            else:
                print(f"[WARNING] Unsupported mime type: {mime_type}")
                
    except Exception as e:
        print(f"Error in client_to_agent_messaging: {e}")
        raise


@app.get("/")
async def root():
    """Serves the main index.html page"""
    index_path = STATIC_DIR / "index.html"
    print(f"Attempting to serve index.html from: {index_path}")
    print(f"File exists: {index_path.exists()}")
    
    if not index_path.exists():
        return {"error": f"index.html not found at {index_path}", "static_dir": str(STATIC_DIR)}
    return FileResponse(str(index_path))


@app.get("/app.js")
async def serve_app_js():
    """Serves the app.js file as an ES module"""
    # Check in static/js/ directory
    js_path = STATIC_DIR / "js" / "app.js"
    
    if js_path.exists():
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/javascript; charset=utf-8"
        )
    
    return Response(
        content=f"console.error('app.js not found at {js_path}');",
        status_code=404,
        media_type="application/javascript"
    )


@app.get("/vite.svg")
async def serve_vite_svg():
    """Serves the vite.svg icon if it exists"""
    svg_path = STATIC_DIR / "vite.svg"
    if svg_path.exists():
        return FileResponse(str(svg_path), media_type="image/svg+xml")
    # Return 404 for missing optional icon
    return Response(status_code=404)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, is_audio: str = "false"):
    """
    WebSocket endpoint for client connections.
    
    Args:
        websocket (WebSocket): The WebSocket connection
        user_id (int): Unique client identifier
        is_audio (str): Audio mode flag (not used in text-only mode)
    """
    # Accept WebSocket connection
    await websocket.accept()
    print(f"Client #{user_id} connected, text mode only")
    
    try:
        # Start agent session (text-only)
        user_id_str = str(user_id)
        live_events, live_request_queue = await start_agent_session(
            user_id_str, 
            is_audio=False  # Always False for text-only
        )
        
        # Create concurrent tasks for bidirectional communication
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, live_request_queue)
        )
        
        # Wait for either task to complete (or error)
        tasks = [agent_to_client_task, client_to_agent_task]
        done, pending = await asyncio.wait(
            tasks, 
            return_when=asyncio.FIRST_EXCEPTION
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            
        # Check if any task raised an exception
        for task in done:
            if task.exception():
                print(f"Task error: {task.exception()}")
                
    except Exception as e:
        print(f"WebSocket error for client #{user_id}: {e}")
    finally:
        # Close LiveRequestQueue
        if 'live_request_queue' in locals():
            live_request_queue.close()
        
        print(f"Client #{user_id} disconnected")


# Run the application
if __name__ == "__main__":
    import uvicorn
    # Use port 8080 for Google Cloud Shell compatibility
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

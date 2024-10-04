import os
import time
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Initializing
bob_asstnt = "asst_AOeSXteKtNbyPAcb0ZPQiLZJ"
private_bob_asstnt = "asst_JWrQIE1b2lNim96pVXr3cCNj"
gate_pwd = "973808"

# Initialize FastAPI app
app = FastAPI(
    title="OpenAI Threaded Assistant",
    description="API for interacting with OpenAI threaded assistant ",
    version="1.0.0"
)

# Allowing CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

# In-memory store for session/thread data
threads_store = {}

# Pydantic model for user input in POST request
class UserInput(BaseModel):
    session_id: str  # The session ID to track conversation threads
    user_input: str

# Root endpoint
@app.get("/api/")
async def read_root():
    return {"message": "Welcome to the OpenAI Threaded Assistant API! {new_version}"}

# POST endpoint to handle user input and interact with OpenAI threads
@app.post("/api/ask")
async def ask_openai(user_input: UserInput):
    try:
        # Check if the session exists, if not, create a new thread
        if user_input.session_id not in threads_store:
            # Create a new thread for the session
            Chat = client.beta.threads.create(messages=[])
            thread_id = Chat.id
            # Initialize the session data
            session_data = {
                'thread_id': thread_id,
                'use_private_assistant': False
            }
            threads_store[user_input.session_id] = session_data
            print(f"New Thread Created for session {user_input.session_id}: {thread_id}")
        else:
            # Retrieve the session data
            session_data = threads_store[user_input.session_id]
            thread_id = session_data['thread_id']
            print(f"Continuing Thread for session {user_input.session_id}: {thread_id}")

        # Append the user's message to the thread
        msg = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input.user_input
        )

        # If gate_pwd is in user_input, set use_private_assistant to True
        if gate_pwd in user_input.user_input:
            session_data['use_private_assistant'] = True
            print(f"Gate password detected. Session {user_input.session_id} elevated to use private assistant.")

        # Determine which assistant ID to use based on the session's 'use_private_assistant' flag
        if session_data['use_private_assistant']:
            assist_id = private_bob_asstnt
            print(f"Using Private-Bob bot for session {user_input.session_id}")
        else:
            assist_id = bob_asstnt
            print(f"Using Bob for session {user_input.session_id}")

        # Create a run with the selected assistant
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assist_id)

        # Wait for the run to complete
        while run.status != "completed":
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Retrieve the latest assistant message
        message_response = client.beta.threads.messages.list(thread_id=thread_id)
        messages = message_response.data

        # Fetch the latest response from the assistant
        latest_message = messages[0]
        assistant_response = latest_message.content[0].text.value

        # Return the assistant's response
        return {"session_id": user_input.session_id, "response": assistant_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

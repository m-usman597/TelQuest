import os
import time
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Load Tavily API key from environment variables and initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key)

# Initializing assistant IDs and gate password
bob_asstnt = "asst_AOeSXteKtNbyPAcb0ZPQiLZJ"
private_bob_asstnt = "asst_JWrQIE1b2lNim96pVXr3cCNj"
gate_pwd = "973808"

# Initialize FastAPI app
app = FastAPI(
    title="OpenAI Threaded Assistant",
    description="API for interacting with OpenAI threaded assistant",
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

# Function to perform a Tavily search
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result

# Function to handle tool output submission
# Function to handle tool output submission
async def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "tavily_search":
            output = tavily_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    # Ensure we're passing the correct required arguments
    if tool_output_array:
        return await asyncio.to_thread(
            client.beta.threads.runs.submit_tool_outputs,
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_output_array
        )
    else:
        return None


# Function to wait for a run to complete asynchronously
async def wait_for_run_completion(thread_id, run_id):
    while True:
        await asyncio.sleep(1)  # Asynchronous sleep to avoid blocking
        run = await asyncio.to_thread(client.beta.threads.runs.retrieve, thread_id=thread_id, run_id=run_id)
        print(f"Current run status: {run.status}")
        if run.status in ['completed', 'failed', 'requires_action']:
            return run

# Root endpoint
@app.get("/api/")
async def read_root():
    return {"message": "Welcome to the OpenAI Threaded Assistant API!"}

@app.post("/api/ask")
@app.post("/api/ask")
async def ask_openai(user_input: UserInput):
    try:
        # Check if the session exists, if not, create a new thread
        if user_input.session_id not in threads_store:
            # Create a new thread for the session
            Chat = await asyncio.to_thread(client.beta.threads.create, messages=[])
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

        # Clear previous messages in the thread to prevent old context from affecting the new input
        message_response = await asyncio.to_thread(client.beta.threads.messages.list, thread_id=thread_id)
        messages = message_response.data

        for msg in messages:
            await asyncio.to_thread(client.beta.threads.messages.delete, thread_id=thread_id, message_id=msg.id)

        # Append the user's new message to the thread
        await asyncio.to_thread(
            client.beta.threads.messages.create,
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
        run = await asyncio.to_thread(client.beta.threads.runs.create, thread_id=thread_id, assistant_id=assist_id)

        # Wait for the run to complete, and handle any required actions
        while True:
            run = await wait_for_run_completion(thread_id, run.id)

            if run.status == 'failed':
                raise HTTPException(status_code=500, detail=f"Run failed: {run.error}")
            elif run.status == 'requires_action':
                # Only handle tool outputs for assistant Bob
                if assist_id == bob_asstnt:
                    run = await submit_tool_outputs(thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)
                else:
                    raise HTTPException(status_code=500, detail="Run requires action but tools are not handled for this assistant.")
            else:
                # Exit the loop when the run is completed successfully
                break

        # Retrieve the latest assistant message after the run is completed
        message_response = await asyncio.to_thread(client.beta.threads.messages.list, thread_id=thread_id)
        messages = message_response.data

        # Fetch the latest response from the assistant
        assistant_messages = [msg for msg in messages if msg.role == 'assistant']
        if assistant_messages:
            latest_message = assistant_messages[-1]
            assistant_response = latest_message.content
        else:
            assistant_response = "No response from the assistant."

        # Return the assistant's response
        return {"session_id": user_input.session_id, "response": assistant_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

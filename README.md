
OpenAI Threaded Assistant API
Overview
This project is an API built using FastAPI that interacts with OpenAI's threaded assistant. It enables users to maintain conversation threads through an API, leveraging OpenAI's language models to respond to user queries based on a session ID. The API provides an endpoint for interacting with OpenAI models while maintaining conversation history across multiple sessions.

Features
Threaded Conversations: Each session ID maintains its own conversation thread with OpenAI, allowing continuous dialogue.
Multiple Assistants: The API supports switching between two assistants, "Bob" and "Private-Bob," based on a password found in user input.
Session Management: Sessions are stored in memory, allowing users to maintain context across multiple API requests.
CORS Support: The app allows cross-origin resource sharing (CORS) for easy integration with web clients.
Technologies Used
FastAPI: A high-performance Python framework for building APIs.
OpenAI API: Integration with OpenAI for threaded conversations.
Pydantic: For data validation in API requests.
dotenv: For managing environment variables securely.
CORS Middleware: To handle cross-origin requests.
Getting Started
Prerequisites
Python 3.8+
OpenAI API Key
.env file with the OpenAI API key (OPENAI_API_KEY)
Installation
Clone the repository:

bash
Copy code
git clone <repository_url>
cd <project_directory>
Install the required packages:

bash
Copy code
pip install -r requirements.txt
Create a .env file: In the project root, create a .env file and add the following:

bash
Copy code
OPENAI_API_KEY=your_openai_api_key_here
Run the FastAPI app:

bash
Copy code
uvicorn main:app --reload
The app will start on http://127.0.0.1:8000.

Endpoints
Root Endpoint

URL: /
Method: GET
Description: Returns a welcome message.
Response:
json
Copy code
{
  "message": "Welcome to the OpenAI Threaded Assistant API!"
}
Ask Assistant

URL: /ask
Method: POST
Description: Sends a user input to OpenAI assistant and receives a response based on the conversation thread.
Request Body:
json
Copy code
{
  "session_id": "string",
  "user_input": "string"
}
Response:
json
Copy code
{
  "session_id": "string",
  "response": "string"
}
Example Request
You can send a POST request to /ask to interact with the assistant:

bash
Copy code
curl -X 'POST' \
  'http://127.0.0.1:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_id": "12345",
  "user_input": "Hello, how are you?"
}'
Configuration
Assistant IDs:

The app uses two assistants: Bob and Private-Bob.
To use Private-Bob, include the password (973808) in the user input.
Environment Variables:

Ensure your .env file contains your OpenAI API key under the key OPENAI_API_KEY.
Session Management
Sessions are tracked by the session_id provided in each API request. The API stores conversation threads in an in-memory store for simplicity, but this can be replaced with a persistent database for production use.
CORS
The app allows requests from any origin using the following configuration:

python
Copy code
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

Error Handling
If an error occurs during the interaction with the OpenAI API, the server will return a 500 status code with the error message.

Future Improvements
Persistent Storage: Replace the in-memory threads_store with a database for scalability.
Enhanced Security: Add more authentication methods to protect sensitive API endpoints.
Error Handling: Improve error handling mechanisms to provide more user-friendly feedback.
License
This project is licensed under the MIT License.

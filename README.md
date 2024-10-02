# OpenAI Threaded Assistant API

A brief description of what this project does: This API interacts with OpenAI's threaded assistant, maintaining conversational threads with a session-based approach and supports switching between multiple assistants.

## Installation

Creating a virtual environment

```bash
  python -m venv myenv
  myenv/Scripts/Activate
  ```


Install the project with pip

```bash
  pip install -r requirements.txt
  cd <project_directory>
```
## Features
- Threaded Conversations using OpenAI
- Multiple Assistants with Private Access
- In-memory session tracking
- CORS Support for web clients
## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies


```bash
  pip install -r requirements.txt
```

Run the server 

```bash
  uvicorn main:app --reload
```


## API Reference

#### Read Root
```http
    GET /

```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `None` | `None` | Root endpoint returns welcome message |

#### Ask Assistant

```http
    POST /ask

```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `session_id`      | `string` | **Required**.  Session ID to track thread|
| `user_input`      | `string` | **Required**. 	Required. User input for assistant |


#### Example

```bash
  curl -X 'POST' \
  'http://127.0.0.1:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_id": "12345",
  "user_input": "Hello, how are you?"
}'

```




## Features
- Multiple Assistants (Bob and Private-Bob)
- Session-based conversation tracking
- In-memory session storage (easy to extend to a database)




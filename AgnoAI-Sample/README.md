# AgnoAI Sample

This project is a lightweight FastAPI sample that uses the Agno framework to run a multi-agent workflow for software design tasks. A single user prompt is processed by three specialized agents:

- Architect: creates the system design
- Developer: turns the design into an implementation approach
- Tester: produces a focused validation and test plan

The app also gives each agent access to DuckDuckGo web tools so they can pull in external references when helpful.

## Features

- FastAPI API service
- Multi-agent orchestration with Agno
- OpenAI-compatible model integration
- Structured JSON responses for architecture, implementation, and testing output
- Input validation for empty prompts
- Environment-based configuration

## Project structure

- `main.py` — FastAPI app and agent pipeline
- `requirements.txt` — Python dependencies
- `.env` — local environment variables (not committed)
- `.gitignore` — excludes environment and cache files

## Requirements

- Python 3.10 or newer
- An OpenAI-compatible API endpoint and key

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following values:

```env
BASE_URL=https://your-openai-compatible-api-url
API_KEY=your_api_key
MODEL=gpt-4o-mini
```

Replace the values with your actual model provider configuration.

## Running the app

Start the API server with:

```bash
python main.py
```

Or use Uvicorn directly:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The app will run at:

```text
http://127.0.0.1:8000
```

## API usage

### Endpoint

`POST /run`

### Request body

```json
{
  "prompt": "Design a microservice for user authentication and authorization"
}
```

### Example response

```json
{
  "architecture": "...",
  "development": "...",
  "testing": "..."
}
```

### Example with curl

```bash
curl -X POST "http://127.0.0.1:8000/run" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Create a secure API for managing tasks"}'
```

## Notes

- The app validates that the prompt is not empty.
- If `BASE_URL`, `API_KEY`, or `MODEL` is missing, the API returns a 503 error.
- Agent failures are surfaced as HTTP 502 errors for easier debugging.

## License

This project does not include a specific license file. Please check your organization or repository policies before using it in production.

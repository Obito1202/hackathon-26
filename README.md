# Agent Discovery API

This project exposes a small FastAPI application that returns agent and tool metadata, plus a simple command-line client that calls the API.

## Project files

- `test_fastapi.py` — FastAPI app and endpoint definitions
- `agent_discovery_client.py` — CLI client used to call the API
- `requirements.txt` — Python dependencies

## Local run

### 1. Create and activate a virtual environment

```bash
cd /Users/vaibhavjoshi/hackathon-26
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Start the API locally

```bash
python -m uvicorn test_fastapi:app --host 127.0.0.1 --port 8000
```

### 4. Run the client locally

In a second terminal:

```bash
cd /Users/vaibhavjoshi/hackathon-26
source venv/bin/activate
python agent_discovery_client.py
```

The client will call the default URL:

```text
http://127.0.0.1:8000
```

### 5. Run the tests

```bash
python -m pytest -q test_fastapi.py
```

## Online hosting

To host this API online, deploy the FastAPI app to a Python-compatible hosting service such as:

- Render
- Railway
- Fly.io
- Hugging Face Spaces
- Azure App Service

### Recommended hosting pattern

The API app should run with:

```bash
uvicorn test_fastapi:app --host 0.0.0.0 --port 8000
```

If the hosting provider uses a different port, set the app to listen on that port. Many platforms provide this in the environment as `$PORT`.

Example:

```bash
uvicorn test_fastapi:app --host 0.0.0.0 --port ${PORT:-8000}
```

### Deployment steps on Render

1. Push this repository to GitHub.
2. Create a new Web Service on Render.
3. Select the repository.
4. Use the following build settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn test_fastapi:app --host 0.0.0.0 --port 8000`
5. Deploy the service.

Your public API URL will look something like:

```text
https://your-service-name.onrender.com
```

### Client configuration for hosted API

If you want the CLI client to use the online API instead of the local one, set the environment variable:

```bash
export AGENT_DISCOVERY_URL=https://your-service-name.onrender.com
```

Then run:

```bash
python agent_discovery_client.py
```

## Notes

- The local client uses the default base URL `http://127.0.0.1:8000`.
- The hosted client should point to the live API URL using `AGENT_DISCOVERY_URL`.
- The FastAPI app is defined in `test_fastapi.py`, so the startup command must reference that module.

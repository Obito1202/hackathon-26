import ast
import json
import os

import requests


BASE_URL = os.environ.get("AGENT_DISCOVERY_URL", "http://127.0.0.1:8000")


def request_json(method, path, payload=None):
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=payload, timeout=5)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {url}.")
        print("Start the API first with:")
        print("./venv/bin/python -m uvicorn test_fastapi:app --host 127.0.0.1 --port 8000")
        raise SystemExit(1)

    return response.json()


def print_result(label, data):
    print(f"{label}:")
    print(json.dumps(data, indent=2))


def parse_command(command: str):
    parts = command.strip().split(maxsplit=2)
    if len(parts) < 2:
        raise ValueError("Command format should be: GET /agents or PUT /agents/agent-004")

    method = parts[0].upper()
    path = parts[1]
    payload = None

    if method not in {"GET", "PUT"}:
        raise ValueError("Only GET and PUT are supported.")

    if method == "PUT":
        if len(parts) == 3:
            raw_payload = parts[2]
        else:
            raw_payload = input("Enter JSON payload: ").strip()

        if not raw_payload:
            raise ValueError("PUT requires a JSON payload.")

        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            try:
                payload = ast.literal_eval(raw_payload)
            except (ValueError, SyntaxError):
                raise ValueError("PUT payload must be valid JSON or a Python-style dict.")

    return method, path, payload


def main():
    print("Type commands like:")
    print("  GET /agents")
    print("  GET /agents/agent-001")
    print("  GET /tools")
    print("  PUT /agents/agent-004 {'name': 'ops-agent', 'status': 'inactive'}")
    print("  PUT /tools/tool-003 {'name': 'document-parser-tool', 'description': 'Parse and summarize documents'}")
    print("Type 'exit' to quit.\n")

    while True:
        command = input("Enter command: ").strip()
        if command.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        try:
            method, path, payload = parse_command(command)
            result = request_json(method, path, payload)
            if method == "GET" and isinstance(result, list):
                print("Discovered items:")
                for item in result:
                    print(json.dumps(item, indent=2))
            else:
                print_result(f"{method} {path}", result)
        except ValueError as exc:
            print(f"Invalid command: {exc}")
        except requests.HTTPError as exc:
            print(f"Request failed: {exc}")


if __name__ == "__main__":
    main()

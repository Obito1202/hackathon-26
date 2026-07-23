import json
import os

import requests


BASE_URL = os.environ.get("AGENT_DISCOVERY_URL", "http://127.0.0.1:8000")


def fetch_items(resource):
    url = f"{BASE_URL}/{resource}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {url}.")
        print("Start the API first with:")
        print("./venv/bin/python -m uvicorn test_fastapi:app --host 127.0.0.1 --port 8000")
        raise SystemExit(1)

    return response.json()


def print_items(kind, items):
    print(f"Discovered {kind}:")
    for item in items:
        print(json.dumps(item, indent=2))


def main():
    print("Choose what to discover:")
    print("1. Agents")
    print("2. Tools")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        items = fetch_items("agents")
        print_items("agents", items)
    elif choice == "2":
        items = fetch_items("tools")
        print_items("tools", items)
    else:
        print("Invalid choice. Please enter 1 or 2.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

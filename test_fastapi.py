from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


AGENTS = [
    {
        "id": "agent-001",
        "name": "assistant-agent",
        "description": "General assistant agent for common support tasks",
        "status": "active",
        "owner": "platform-team",
        "category": "support",
        "version": "1.0.0",
        "specs": {
            "purpose": "Handles common user support requests",
            "model": "gpt-4o-mini",
            "runtime": "python",
        },
        "prompt": "Answer user questions clearly and concisely.",
        "tools": ["web-search-tool"],
        "code": "print('assistant agent')",
        "repository": "central-repo/assistant-agent",
        "editable": True,
        "approvals": "pending",
        "comments": ["Needs review for policy coverage"],
        "monitoring": "enabled",
        "usage": 120,
        "subscriptions": "standard",
        "vulnerabilities": "none",
        "certifications": "basic",
    },
    {
        "id": "agent-002",
        "name": "research-agent",
        "description": "Agent for research and summarization workflows",
        "status": "active",
        "owner": "research-team",
        "category": "research",
        "version": "1.1.0",
        "specs": {
            "purpose": "Summarizes and analyzes research documents",
            "model": "gpt-4o",
            "runtime": "python",
        },
        "prompt": "Generate concise summaries with citations.",
        "tools": ["web-search-tool", "code-execution-tool"],
        "code": "print('research agent')",
        "repository": "central-repo/research-agent",
        "editable": True,
        "approvals": "approved",
        "comments": [],
        "monitoring": "enabled",
        "usage": 80,
        "subscriptions": "premium",
        "vulnerabilities": "low",
        "certifications": "advanced",
    },
]


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}


@app.get("/agents")
def discover_agents():
    return AGENTS


@app.get("/agents/{agent_id}")
def get_agent_detail(agent_id: str):
    for agent in AGENTS:
        if agent["id"] == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")


@app.get("/tools")
def discover_tools():
    return [
        {
            "id": "tool-001",
            "name": "web-search-tool",
            "description": "Search the web for up-to-date information",
            "status": "available",
        },
        {
            "id": "tool-002",
            "name": "code-execution-tool",
            "description": "Execute small code snippets in a sandbox",
            "status": "available",
        },
    ]


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI"}


def test_discover_agents():
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "assistant-agent"
    assert "owner" in data[0]
    assert "category" in data[0]
    assert data[0]["specs"]["model"] == "gpt-4o-mini"
    assert data[0]["tools"] == ["web-search-tool"]


def test_get_agent_detail():
    response = client.get("/agents/agent-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "agent-001"
    assert data["name"] == "assistant-agent"
    assert data["specs"]
    assert data["approvals"] == "pending"


def test_discover_tools():
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "web-search-tool"

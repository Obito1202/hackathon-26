from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    owner: str | None = None
    category: str | None = None
    version: str | None = None
    specs: dict | None = None
    prompt: str | None = None
    tools: list[str] | None = None
    code: str | None = None
    repository: str | None = None
    editable: bool | None = None
    approvals: str | None = None
    comments: list[str] | None = None
    monitoring: str | None = None
    usage: int | None = None
    subscriptions: str | None = None
    vulnerabilities: str | None = None
    certifications: str | None = None


class ToolUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


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

TOOLS = [
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


@app.put("/agents/{agent_id}")
def update_agent_detail(agent_id: str, payload: AgentUpdate):
    for agent in AGENTS:
        if agent["id"] == agent_id:
            for key, value in payload.model_dump(exclude_unset=True).items():
                agent[key] = value
            return agent

    new_agent = {
        "id": agent_id,
        "name": payload.name or "",
        "description": payload.description or "",
        "status": payload.status or "active",
        "owner": payload.owner or "unknown",
        "category": payload.category or "general",
        "version": payload.version or "1.0.0",
        "specs": payload.specs or {},
        "prompt": payload.prompt or "",
        "tools": payload.tools or [],
        "code": payload.code or "",
        "repository": payload.repository or "",
        "editable": payload.editable if payload.editable is not None else True,
        "approvals": payload.approvals or "pending",
        "comments": payload.comments or [],
        "monitoring": payload.monitoring or "enabled",
        "usage": payload.usage if payload.usage is not None else 0,
        "subscriptions": payload.subscriptions or "standard",
        "vulnerabilities": payload.vulnerabilities or "none",
        "certifications": payload.certifications or "basic",
    }
    AGENTS.append(new_agent)
    return new_agent


@app.get("/tools")
def discover_tools():
    return TOOLS


@app.get("/tools/{tool_id}")
def get_tool_detail(tool_id: str):
    for tool in TOOLS:
        if tool["id"] == tool_id:
            return tool
    raise HTTPException(status_code=404, detail="Tool not found")


@app.put("/tools/{tool_id}")
def update_tool_detail(tool_id: str, payload: ToolUpdate):
    for tool in TOOLS:
        if tool["id"] == tool_id:
            for key, value in payload.model_dump(exclude_unset=True).items():
                tool[key] = value
            return tool

    new_tool = {
        "id": tool_id,
        "name": payload.name or "",
        "description": payload.description or "",
        "status": payload.status or "available",
    }
    TOOLS.append(new_tool)
    return new_tool


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


def test_get_tool_detail():
    response = client.get("/tools/tool-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tool-001"
    assert data["name"] == "web-search-tool"
    assert data["status"] == "available"


def test_discover_tools():
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "web-search-tool"


def test_put_agent_detail():
    response = client.put(
        "/agents/agent-004",
        json={
            "name": "ops-agent",
            "status": "inactive",
            "owner": "ops-team",
            "category": "operations",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "agent-004"
    assert data["name"] == "ops-agent"
    assert data["status"] == "inactive"
    assert data["owner"] == "ops-team"
    assert data["category"] == "operations"


def test_put_tool_detail():
    response = client.put(
        "/tools/tool-003",
        json={
            "name": "document-parser-tool",
            "description": "Parse and summarize documents",
            "status": "available",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tool-003"
    assert data["name"] == "document-parser-tool"
    assert data["description"] == "Parse and summarize documents"
    assert data["status"] == "available"

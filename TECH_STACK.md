# Technical Stack Documentation

**Last Updated:** January 15, 2026

This document explains the technical stack used in this project: how ADK, AG-UI, and CopilotKit work together.

---

## Table of Contents

1. [Overview](#overview)
2. [ADK (Agent Development Kit)](#adk-agent-development-kit)
3. [AG-UI Protocol](#ag-ui-protocol)
4. [CopilotKit](#copilotkit)
5. [Integration Pattern](#integration-pattern)
6. [Key Concepts](#key-concepts)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Our stack connects three technologies:

```
CopilotKit (Frontend UI)
    ↓
AG-UI Protocol (Communication Layer)
    ↓
ADK (Agent Backend)
    ↓
OpenAI (LLM)
```

**Why this stack:**
- **ADK**: Google's official framework for building AI agents with tools and memory
- **AG-UI**: Open protocol that connects frontends to ADK agents
- **CopilotKit**: React UI framework for chat interfaces that supports AG-UI

---

## ADK (Agent Development Kit)

### What It Is

Google's Python framework for building AI agents. Similar to LangChain but designed specifically for agent workflows.

**Official Docs:** https://google.github.io/adk-docs/

### Key Concepts

#### 1. Agent Classes

```python
from google.adk.agents import LlmAgent

# LlmAgent is the main class for AI agents
root_agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-4-turbo-preview"),
    name="my_agent",  # Must be valid Python identifier
    instruction="You are a helpful assistant.",
    tools=[...]  # Optional tools/MCP servers
)
```

**Important:**
- `LlmAgent` and `Agent` are the same (Agent is a type alias)
- Variable name `root_agent` is the convention for exposing agents via AG-UI
- Agent `name` must be a valid Python identifier (letters, numbers, underscores only)

#### 2. Class Hierarchy

```
BaseAgent (abstract)
├── LlmAgent (aka Agent) ← Use this for AI agents
├── LoopAgent
├── SequentialAgent
└── ParallelAgent
```

#### 3. Models

ADK supports multiple LLM providers through adapters:

```python
from google.adk.models.lite_llm import LiteLlm

# Use LiteLLM adapter for OpenAI
model = LiteLlm(model="openai/gpt-4-turbo-preview")
```

**Why LiteLLM:**
- Allows using OpenAI models with ADK
- Unified interface for multiple LLM providers
- Required because ADK defaults to Google's Gemini

#### 4. Tools Integration

ADK supports tools through MCP (Model Context Protocol):

```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Example: Kubernetes MCP server
kubernetes_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "kubernetes-mcp-server"],
            env={"KUBECONFIG": "/path/to/kubeconfig"}
        )
    )
)

root_agent = LlmAgent(
    model=...,
    tools=[kubernetes_toolset]
)
```

#### 5. Sessions (Deprecated for AG-UI)

**Note:** When using AG-UI, you don't manually manage sessions. The following is for reference only:

```python
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Manual session management (NOT needed with AG-UI)
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="myapp", session_service=session_service)
```

### Package Requirements

```toml
[tool.poetry.dependencies]
google-adk = "*"       # ADK framework
litellm = "*"          # For OpenAI integration
openai = "*"           # OpenAI SDK
```

---

## AG-UI Protocol

### What It Is

AG-UI (Agent User Interface) is an open protocol that connects web frontends to ADK agents.

**Official Docs:** https://google.github.io/adk-docs/tools/third-party/ag-ui/

### Why It Exists

**Problem:** ADK agents run in Python, web UIs run in JavaScript. How do they talk?

**Solution:** AG-UI provides a standardized protocol so any frontend framework (React, Vue, etc.) can communicate with any ADK agent.

### Backend (Python)

**Package:** `ag-ui-adk`

```python
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

app = FastAPI()

# Wrap the ADK agent with AG-UI middleware
adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="my_app",
    user_id="default_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Expose the wrapped agent via AG-UI protocol
add_adk_fastapi_endpoint(app, adk_agent, path="/")
```

**What `add_adk_fastapi_endpoint()` does:**
1. Creates AG-UI protocol endpoints automatically
2. Handles agent discovery (`/info` endpoint)
3. Manages conversation state
4. Streams responses to frontend
5. Translates between AG-UI protocol and ADK agent API

**No manual endpoints needed!** This replaces writing custom `/chat` or `/copilotkit` endpoints.

### Frontend (TypeScript)

**Package:** `@ag-ui/client`

```typescript
import { HttpAgent } from "@ag-ui/client";

// Points to your backend root URL
const agent = new HttpAgent({ url: "http://localhost:8000/" });
```

**What `HttpAgent` does:**
1. Discovers available agents from backend
2. Sends messages using AG-UI protocol
3. Receives streaming responses
4. Handles errors and reconnection

### Protocol Details

AG-UI uses these endpoints (auto-created by `add_adk_fastapi_endpoint`):

- `GET /info` - Agent discovery (returns agent name, capabilities)
- `POST /` - Send messages to agent
- `WebSocket /ws` - Streaming responses (optional)

**You don't create these manually.** `add_adk_fastapi_endpoint()` does it for you.

---

## CopilotKit

### What It Is

React framework for building AI chat interfaces. Like Vercel AI SDK but more opinionated with pre-built UI components.

**Official Docs:** https://docs.copilotkit.ai/

### Key Components

#### 1. CopilotKit Provider

Wraps your app and provides agent context:

```typescript
import { CopilotKit } from "@copilotkit/react-core";

<CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent">
  {/* Your app */}
</CopilotKit>
```

**Props:**
- `runtimeUrl`: Next.js API route that connects to backend
- `agent`: Name of the ADK agent to use (must match backend agent name)

#### 2. CopilotPopup

Chat popup in bottom-right corner:

```typescript
import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

<CopilotPopup
  instructions="You are a helpful assistant."
  labels={{
    title: "Chat Assistant",
    initial: "Hi! How can I help?"
  }}
/>
```

#### 3. CopilotSidebar

Full sidebar chat interface:

```typescript
import { CopilotSidebar } from "@copilotkit/react-ui";

<CopilotSidebar
  defaultOpen={true}
  clickOutsideToClose={false}
  labels={{...}}
/>
```

### Runtime Integration

**File:** `app/api/copilotkit/route.ts`

```typescript
import { CopilotRuntime, ExperimentalEmptyAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

const BACKEND_URL = "http://localhost:8000";

// Empty adapter for single-agent setup
const serviceAdapter = new ExperimentalEmptyAdapter();

// Connect to ADK agent via AG-UI
const runtime = new CopilotRuntime({
  agents: {
    my_agent: new HttpAgent({ url: `${BACKEND_URL}/` })
  }
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit"
  });
  return handleRequest(req);
};
```

**Important:**
- Agent name in `agents: { my_agent: ... }` must match backend agent name
- HttpAgent URL points to backend **root**, not a specific endpoint
- `ExperimentalEmptyAdapter` is for single-agent setups (use other adapters for multi-agent)

### Package Requirements

```json
{
  "dependencies": {
    "@ag-ui/client": "latest",
    "@copilotkit/react-core": "latest",
    "@copilotkit/react-ui": "latest",
    "@copilotkit/runtime": "latest"
  }
}
```

---

## Integration Pattern

### Complete Flow

```
User types message in CopilotPopup
    ↓
CopilotKit sends to /api/copilotkit (Next.js API route)
    ↓
CopilotRuntime forwards to HttpAgent
    ↓
HttpAgent sends via AG-UI protocol to backend
    ↓
add_adk_fastapi_endpoint receives message
    ↓
ADK root_agent processes with OpenAI
    ↓
Response streams back through AG-UI
    ↓
CopilotKit displays in chat UI
```

### Minimal Working Example

**Backend (`main.py`):**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

root_agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-4-turbo-preview"),
    name="my_agent",
    instruction="You are a helpful assistant."
)

# Wrap with ADKAgent before exposing via AG-UI
adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="my_app",
    user_id="default_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

add_adk_fastapi_endpoint(app, adk_agent, path="/")
```

**Frontend (`app/api/copilotkit/route.ts`):**

```typescript
import { CopilotRuntime, ExperimentalEmptyAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

const serviceAdapter = new ExperimentalEmptyAdapter();

const runtime = new CopilotRuntime({
  agents: {
    my_agent: new HttpAgent({ url: "http://localhost:8000/" })
  }
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit"
  });
  return handleRequest(req);
};
```

**Frontend (`app/page.tsx`):**

```typescript
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="my_agent">
      <main>
        <h1>My App</h1>
        <CopilotPopup
          instructions="You are a helpful assistant."
          labels={{ title: "Assistant", initial: "Hi!" }}
        />
      </main>
    </CopilotKit>
  );
}
```

That's it! No custom endpoints, no manual session management.

---

## Key Concepts

### 1. Agent Names Must Match

```python
# Backend
root_agent = LlmAgent(name="my_agent", ...)
```

```typescript
// Frontend
agents: { my_agent: new HttpAgent(...) }
```

```typescript
// Frontend
<CopilotKit agent="my_agent">
```

**All three must use the same name.**

### 2. URL Conventions

- Backend runs on: `http://localhost:8000`
- Frontend runs on: `http://localhost:8080`
- HttpAgent points to backend **root**: `http://localhost:8000/`
- CopilotKit points to Next.js route: `/api/copilotkit`

### 3. CORS Configuration

Backend must allow frontend origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### 4. Environment Variables

**Backend (`.env`):**
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
CORS_ORIGINS=http://localhost:8080
```

**Frontend (`.env.local`):**
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 5. No Manual Endpoints

**❌ Don't do this:**
```python
@app.post("/chat")
async def chat(message: str):
    # Manual endpoint - NOT needed with AG-UI
    ...
```

**✅ Do this:**
```python
# Wrap your agent
adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="my_app",
    user_id="default_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Expose via AG-UI
add_adk_fastapi_endpoint(app, adk_agent, path="/")  # Handles everything
```

---

## Troubleshooting

### "'LlmAgent' object has no attribute 'run'"

**Cause:** Passing raw LlmAgent to `add_adk_fastapi_endpoint` instead of wrapping it with `ADKAgent`.

**Fix:**
```python
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

# Wrap the agent first
adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="my_app",
    user_id="default_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Then expose it
add_adk_fastapi_endpoint(app, adk_agent, path="/")
```

### "Agent not found after runtime sync"

**Cause:** Agent name mismatch or backend not exposing agent properly.

**Fix:**
1. Check agent names match everywhere
2. Verify agent is wrapped with `ADKAgent` before passing to `add_adk_fastapi_endpoint`
3. Check backend is running on correct port
4. Verify CORS allows frontend origin

### "Failed to create MCP session"

**Cause:** MCP tool server not running or npx not installed.

**Fix:**
1. Check if npx is installed: `which npx`
2. Verify MCP server command is correct
3. Comment out MCP tools if testing basic agent first

### "Import errors in IDE"

**Cause:** IDE doesn't see Poetry virtualenv or node_modules.

**Fix:**
- Python: Run with `poetry run python ...`
- TypeScript: Restart TypeScript server in IDE
- These are IDE issues, code will work when run

### Backend not starting

**Cause:** Missing dependencies.

**Fix:**
```bash
cd backend
poetry install  # Installs all dependencies including ag-ui-adk
```

### Frontend not connecting

**Cause:** Missing AG-UI client package.

**Fix:**
```bash
cd frontend
npm install  # Installs @ag-ui/client and other deps
```

---

## Learning Resources

**ADK:**
- Official Docs: https://google.github.io/adk-docs/
- AG-UI Integration: https://google.github.io/adk-docs/tools/third-party/ag-ui/

**CopilotKit:**
- Official Docs: https://docs.copilotkit.ai/
- ADK Guide: https://docs.copilotkit.ai/adk

**Examples:**
- Starter Template: https://github.com/CopilotKit/with-adk
- Quick Start: `npx create-ag-ui-app@latest --adk`

**Blog Posts:**
- [Build a Frontend for ADK Agents with AG-UI](https://www.copilotkit.ai/blog/build-a-frontend-for-your-adk-agents-with-ag-ui)
- [Delight users by combining ADK Agents with Frontends using AG-UI](https://developers.googleblog.com/delight-users-by-combining-adk-agents-with-fancy-frontends-using-ag-ui/)

---

## Version History

- **v1.0** (Jan 15, 2026): Initial documentation based on Phase 2 implementation

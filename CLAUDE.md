# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Scruffy - The Cluster Janitor**: An AI-powered assistant for managing and troubleshooting Kubernetes/OpenShift clusters using natural language.

Built with Google's Agent Development Kit (ADK) using a multi-agent architecture where a router agent delegates queries to 5 specialized agents, each with its own expertise and MCP (Model Context Protocol) server connections.

This is a **proof of concept** focused on readability and simplicity over production robustness.

## Commands

### Backend (Python + Poetry)

```bash
# Setup
cd backend
poetry install

# Development server (auto-reload, port 8000)
poetry run dev

# Health check
curl http://localhost:8000/health

# Agent discovery (AG-UI protocol)
curl http://localhost:8000/api/chat/info
```

### Frontend - PatternFly UI (Primary, Production)

```bash
cd source/observability-assistant-ui
make install
make dev  # Port 3000
```

### Frontend - CopilotKit (Development/Reference)

```bash
cd frontend
npm install
npm run dev  # Port 8080
```

### MCP Servers (External, Required)

These run outside this repo and must be started separately:

```bash
# Kubernetes MCP (port 8001)
npx kubernetes-mcp-server@latest --port 8001 --kubeconfig ~/.kube/config

# Observability MCP (port 8002)
cd source/obs-mcp
go run ./cmd/obs-mcp/ --listen 127.0.0.1:8002 --auth-mode kubeconfig --metrics-backend prometheus --insecure

# Incident Detection MCP (port 8003)
kubectl port-forward -n openshift-cluster-observability-operator svc/cluster-health-mcp-server 8003:8085

# Insights MCP (port 8004)
kubectl port-forward -n insights-results-mcp svc/insights-results-mcp-server 8004:5000
```

### Testing

```bash
# Full stack integration test
# Terminal 1: cd backend && poetry run dev
# Terminal 2: cd source/observability-assistant-ui && make dev
# Terminal 3-6: Start each MCP server
# Browser: http://localhost:3000
```

## Architecture

### Multi-Agent System

```
Frontend (PatternFly :3000 or CopilotKit :8080)
    ↓
AG-UI Protocol (SSE streaming at /api/chat)
    ↓
Backend FastAPI (:8000)
    ↓
Router Agent (root_agent in agent/agent.py)
    ├─→ Kubernetes Agent → kubernetes-mcp (:8001)
    ├─→ Metrics Agent → obs-mcp (:8002) + graph_timeseries_data tool
    ├─→ Incident Detection Agent → cluster-health-mcp (:8003)
    ├─→ Insights Agent → insights-results-mcp (:8004)
    └─→ OpenShift Docs Agent → Google Search (Gemini)
        ↓
    OpenAI GPT-4 (main agents) / Gemini (docs agent)
```

### Agent Files

All agents in `backend/agent/`:

1. **`agent.py`**: Router agent (`root_agent`) - orchestrates delegation
   - Uses `sub_agents` parameter for event propagation to frontend
   - Wraps docs agent as `AgentTool` to isolate google_search from function calling
   - Agent name: `openshift_router` (but exposed as `openshift_assistant`)

2. **`kubernetes_agent.py`**: Cluster resources (pods, logs, events)
   - Uses `McpToolset` connected to kubernetes-mcp-server (:8001)
   - Enforces query scoping (prevents overly broad queries)

3. **`metrics_agent.py`**: Prometheus/Thanos metrics
   - Uses `McpToolset` connected to obs-mcp-server (:8002)
   - Custom `graph_timeseries_data` tool for charting (uses httpx)
   - MANDATORY workflow: list_metrics → get_label_names → get_label_values → query

4. **`incident_detection_agent.py`**: Cluster health incidents
   - Uses `McpToolset` connected to cluster-health-mcp (:8003)
   - Requires Bearer token auth: `kubernetes-authorization: Bearer {token}`

5. **`insights_agent.py`**: Red Hat Insights recommendations
   - Uses `McpToolset` connected to insights-results-mcp (:8004)
   - No authentication required

6. **`openshift_docs_agent.py`**: Official OpenShift 4.20 docs search
   - Uses native Gemini model (not LiteLLM) with `google_search` tool
   - Wrapped as `AgentTool` in router to avoid function calling conflicts
   - ALWAYS uses `site:docs.redhat.com/en/documentation/openshift_container_platform/4.20`

### Key Integration Points

**Backend (`main.py`):**
```python
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="openshift_assistant",  # Must match frontend
    user_id="default_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

add_adk_fastapi_endpoint(app, adk_agent, path="/api/chat")  # Auto-generates endpoints
```

**Frontend (CopilotKit `route.ts`):**
```typescript
const runtime = new CopilotRuntime({
  agents: {
    openshift_assistant: new HttpAgent({ url: `${BACKEND_URL}/api/chat` })
  }
});
```

**Agent name must match:** `openshift_assistant` in both backend config and frontend.

### Configuration (`backend/config.py`)

Required environment variables in `backend/.env`:
- `OPENAI_API_KEY` - For main agents (GPT-4)
- `GOOGLE_API_KEY` - For docs agent (Gemini + google_search)

Optional:
- `OPENAI_MODEL` - Default: gpt-5-nano
- `GEMINI_MODEL` - Default: gemini-2.5-flash
- `OPENSHIFT_USER_TOKEN` - For incident detection MCP auth (Bearer token)
- `CORS_ORIGINS` - Default: http://localhost:3000,http://localhost:8080

### Sub-Agents Pattern (Current)

Router uses `sub_agents` parameter instead of `AgentTool` for better event propagation to frontend:

```python
root_agent = LlmAgent(
    sub_agents=[kubernetes_agent, metrics_agent, incident_detection_agent, insights_agent],
    tools=[docs_tool],  # Docs agent wrapped as AgentTool due to google_search constraints
)
```

**Why sub_agents?**
- Shares `InvocationContext` between router and sub-agents
- Enables frontend to see sub-agent tool calls in real-time
- TODO: Will switch back to `AgentTool` once ADK PR #3991 merges (adds event streaming to AgentTool)

**Why docs agent is AgentTool?**
- `google_search` tool cannot work in `sub_agents` due to function calling conflicts
- Wrapping as `AgentTool` isolates it from function calling

### Custom Tools (`backend/agent/tools/`)

**`graph_timeseries.py`**:
- Wraps obs-mcp's `execute_range_query` for frontend visualization
- Uses `httpx` to call obs-mcp HTTP endpoint directly
- Returns Prometheus matrix data formatted for Victory.js charts
- Exposed to metrics agent via tools list

## Critical Development Principles

### Minimal Code Philosophy

**This is a proof of concept that will be read frequently.**

- ✅ ONLY implement features explicitly requested
- ❌ DO NOT add features "just in case"
- ❌ DO NOT future-proof the code
- ✅ Keep the codebase as small and readable as possible

### Strict Change Protocol

1. Do EXACTLY what is requested - nothing more
2. Do not add: extra error handling, configuration options, helper functions, comments about future uses
3. Ask before adding anything beyond the request

### Agent Instructions

All agent instructions should be:
- Short, precise, and actionable (no verbose explanations)
- Instructions may include critical behavioral rules (e.g., metrics agent's MANDATORY workflow)
- Router distinguishes: LIVE CLUSTER INVESTIGATION vs DOCUMENTATION SEARCH

### Frontend Development

**IMPORTANT: The user has NO frontend development experience.**

When making frontend changes:
1. Explain in detail BEFORE making changes (what, why, alternatives)
2. After making changes, explain what was changed and how to verify
3. Use simple language - avoid jargon without explanation

### Testing Before Complexity

1. Implement the requested feature
2. Test that it works
3. Document what was added
4. Get user confirmation before moving to next feature

Do not: implement multiple features at once, move to next phase without verification, add "related improvements"

## Common Patterns

### Adding a New Agent

1. Create `backend/agent/new_agent.py`:
```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from config import config

# MCP connection
toolset = McpToolset(connection_params=StreamableHTTPConnectionParams(url="..."))

# Agent definition
new_agent = LlmAgent(
    model=LiteLlm(model=f"openai/{config.OPENAI_MODEL}"),
    name="new_expert",
    description="...",  # Used by router for delegation
    instruction="...",  # Agent's system prompt
    tools=[toolset],
)
```

2. Import and add to router in `agent/agent.py`:
```python
from .new_agent import new_agent

root_agent = LlmAgent(
    sub_agents=[..., new_agent],  # Add to sub_agents list
    tools=[docs_tool],
)
```

3. Update router instruction to include new agent in routing logic

### MCP Tool Integration

MCP servers expose tools dynamically via HTTP:
```python
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8001/mcp",
        headers={"kubernetes-authorization": f"Bearer {token}"} if auth_required else {}
    )
)
```

Agent discovers and uses all tools provided by the MCP server automatically.

### Process Management

When starting background processes (use subshell for proper signal handling):

```bash
# Start
( poetry run dev > /tmp/backend.log 2>&1 ) &
SUBSHELL_PID=$!

# Graceful shutdown (SIGINT, like CTRL+C)
kill -INT $SUBSHELL_PID
sleep 2
ps -p $SUBSHELL_PID 2>/dev/null || echo "Shutdown complete"
```

Signals:
- `kill -INT` or `kill -2`: Graceful (like CTRL+C)
- `kill -9`: Forceful (last resort, no cleanup)

### Git Commits

Only create commits when requested. Follow the git safety protocol in the existing CLAUDE.md.

Critical:
- ALWAYS create NEW commits
- NEVER use `git commit --amend` unless explicitly requested
- NEVER skip hooks (`--no-verify`)
- Include Co-Authored-By line when committing

## Technical References

See also:
- **TECH_STACK.md**: Complete ADK + AG-UI + MCP integration documentation
- **PLANNER.md**: Phase definitions and acceptance criteria (if exists)
- **PLAYWRIGHT.md**: Frontend testing guide with Playwright MCP

## File Structure

```
backend/
├── agent/
│   ├── agent.py                      # Router agent
│   ├── kubernetes_agent.py           # Cluster operations
│   ├── metrics_agent.py              # Prometheus/Thanos
│   ├── incident_detection_agent.py   # Health analysis
│   ├── insights_agent.py             # Red Hat Insights
│   ├── openshift_docs_agent.py       # Documentation search
│   └── tools/
│       └── graph_timeseries.py       # Custom charting tool
├── main.py                           # FastAPI + AG-UI endpoint
└── config.py                         # Environment configuration

frontend/                             # Next.js + CopilotKit (development)
├── app/
│   ├── page.tsx                      # Main chat UI
│   └── api/copilotkit/route.ts       # AG-UI client connection

source/observability-assistant-ui/   # PatternFly UI (production)
```

## Debugging

1. Check backend logs: `tail -f /tmp/backend.log` or check task output
2. Check frontend console (user reports errors)
3. Verify MCP servers are running on correct ports (8001-8004)
4. Test AG-UI discovery: `curl http://localhost:8000/api/chat/info`
5. Fix root cause, not symptoms

## Golden Rule

**If the user didn't ask for it, don't add it.**

The user values:
1. Minimal, readable code
2. Following instructions exactly
3. Testing before complexity
4. Clear documentation of current state
5. Phased, verified development

This is a proof of concept: Readability > Robustness, Simplicity > Scalability, Working > Perfect.

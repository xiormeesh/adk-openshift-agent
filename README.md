# ADK OpenShift Agent

An AI-powered chatbot for managing Kubernetes/OpenShift clusters using natural language.

## Architecture

- **Backend**: Python ADK agent with OpenAI GPT integration
- **Frontends**:
  - PatternFly UI (port 3000) - Production-ready OpenShift-aligned interface
  - CopilotKit (port 8080) - Development/reference interface
- **MCP Server**: kubernetes-mcp-server (standalone Node.js service) for cluster operations
- **Protocol**: AG-UI for real-time agent-UI communication

## Features

- View cluster resources (pods, deployments, services, namespaces)
- Stream and view pod logs
- Troubleshoot cluster issues with AI assistance
- Natural language interface for cluster management

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) - Python dependency management
- Node.js 18+
- Access to a Kubernetes or OpenShift cluster
- OpenAI API key

## Quick Start

See [docs/QUICK_START.md](docs/QUICK_START.md) for 5-minute setup or [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

### Backend Setup

```bash
cd backend
poetry install
poetry run dev
```

### Frontend Setup

**Option 1: PatternFly UI (Recommended for production)**

The PatternFly frontend provides an OpenShift-aligned interface with advanced features:

```bash
cd source/observability-assistant-ui
make install
make dev
```

Runs on http://localhost:3000

**Option 2: CopilotKit (Development/Reference)**

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:8080

### MCP Server Setup

The kubernetes-mcp-server is a standalone Node.js service:

```bash
npx kubernetes-mcp-server@latest --port 8001 --kubeconfig ~/.kube/config
```

or
```bash
npx kubernetes-mcp-server@latest --port 8001 --kubeconfig /var/lib/miniagent/kubeconfig
```

See [docs/MCP_SERVER.md](docs/MCP_SERVER.md) for detailed instructions.


### Running All Services

You need to run three services:
1. **Terminal 1**: MCP Server (`npx kubernetes-mcp-server@latest --port 8080 --kubeconfig ~/.kube/config`)
2. **Terminal 2**: Backend (`cd backend && poetry run dev`)
3. **Terminal 3**: Frontend (`cd frontend && npm run dev`)

## Frontend Comparison

| Feature | PatternFly UI | CopilotKit |
|---------|--------------|------------|
| **Port** | 3000 | 8080 |
| **Technology** | React + Vite + PatternFly 6 | Next.js + CopilotKit |
| **UI Framework** | PatternFly (OpenShift-aligned) | Material-like components |
| **Features** | Prometheus charts, tool visualization, steps, markdown | Basic chat interface |
| **Demo Mode** | Yes (switchable in UI) | No |
| **Production Ready** | Yes | Development/Reference |
| **AG-UI Integration** | Custom SSE implementation | @ag-ui/client library |

Both frontends connect to the same backend at http://localhost:8000 using the AG-UI protocol.

## Project Structure

```
adk-openshift-agent/
├── backend/                          # Python ADK agent
├── frontend/                         # Next.js + CopilotKit UI (port 8080)
├── source/
│   └── observability-assistant-ui/  # PatternFly UI (port 3000)
├── docs/                            # Documentation
├── AG_UI_PROTOCOL.md               # AG-UI endpoint documentation
├── PLAYWRIGHT.md                   # Frontend testing guide
└── README.md
```

## Resources

### Documentation
- [AG-UI Protocol Implementation](AG_UI_PROTOCOL.md) - Backend endpoint documentation
- [Playwright Testing Guide](PLAYWRIGHT.md) - Frontend testing with Playwright MCP

### External
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server)
- [CopilotKit](https://www.copilotkit.ai/)
- [PatternFly Chatbot](https://www.patternfly.org/patternfly-ai/chatbot/overview/)

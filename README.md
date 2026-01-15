# ADK OpenShift Agent

An AI-powered chatbot for managing Kubernetes/OpenShift clusters using natural language.

## Architecture

- **Frontend**: Next.js + React + CopilotKit for interactive chat UI
- **Backend**: Python ADK agent with OpenAI GPT integration
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

```bash
cd frontend
npm install
npm run dev
```

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

## Project Structure

```
adk-openshift-agent/
├── backend/          # Python ADK agent
├── frontend/         # Next.js + CopilotKit UI
├── docs/            # Documentation
└── README.md
```

## Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server)
- [CopilotKit](https://www.copilotkit.ai/)

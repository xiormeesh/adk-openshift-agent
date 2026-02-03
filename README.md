# Openshift Observability AI agents (aka Scruffy - The Cluster Janitor)

<img src="https://preview.redd.it/havent-watched-futurama-in-years-when-did-scruffy-become-a-v0-b2tw503tu6wa1.jpg?auto=webp&s=aef536616a09fc8875a1ebe66c0bfde176df2b1b" width="200" alt="Scruffy the janitor">

*"Scruffy's gonna observe that cluster."*

AI-powered assistant for exploring and troubleshooting Kubernetes/OpenShift clusters. Ask questions in natural language, Scruffy knows what's broken and how to fix it.

Built with Google's Agent Development Kit (ADK) using a multi-agent architecture where specialized agents handle different aspects of cluster management.

## What It Does

Ask questions in plain English, get answers from your cluster:
- **"What pods are in the openshift-monitoring namespace?"** → Kubernetes Agent lists pods
- **"Show me CPU usage for the last hour"** → Metrics Agent queries Prometheus and creates interactive charts
- **"Are there any incidents in my cluster?"** → Incident Detection Agent analyzes cluster health
- **"What does Red Hat Insights recommend?"** → Insights Agent retrieves recommendations
- **"How do I configure persistent volumes in OpenShift?"** → Docs Agent searches official documentation

## Architecture

```
Frontend (PatternFly or CopilotKit)
    ↓
AG-UI Protocol (/api/chat)
    ↓
Router Agent (orchestrator)
    ├─→ Kubernetes Agent → kubernetes-mcp-server (:8001)
    ├─→ Metrics Agent → obs-mcp-server (:8002)
    ├─→ Incident Detection Agent → cluster-health-mcp (:8003)
    ├─→ Insights Agent → insights-results-mcp (:8004)
    └─→ OpenShift Docs Agent → Google Search
```

### Agents

**Router Agent**: Analyzes user queries and delegates to appropriate specialized agent

**Specialized Agents:**
- **Kubernetes**: Cluster resources (pods, logs, deployments, services, events)
- **Metrics**: Prometheus/Thanos queries with interactive time-series charts
- **Incident Detection**: Cluster health analysis and root cause identification
- **Insights**: Red Hat Insights recommendations and configuration validation
- **OpenShift Docs**: Official OpenShift 4.20 documentation search

### MCP Servers

Model Context Protocol servers provide read-only access to cluster data:
- **Port 8001**: kubernetes-mcp-server - Kubernetes/OpenShift resources
- **Port 8002**: obs-mcp-server - Prometheus/Thanos metrics
- **Port 8003**: cluster-health-mcp-server - Incident detection
- **Port 8004**: insights-results-mcp - Red Hat Insights

## Quick Start

### Prerequisites

- Python 3.12, Poetry
- Node.js 24
- OpenAI API key, Google API key
- Kubernetes/OpenShift cluster access

Note: only backend and agents are in this repo, MCP servers need to be fetched from corresponding repos and set up to receive requests (no auth for PoC)

### 1. Backend Setup

```bash
cd backend
poetry install
poetry run dev  # Runs on :8000
```

### 2. Frontend Setup

**Option A: PatternFly UI (Recommended)** - [observability-assistant-ui](https://github.com/falox/observability-assistant-ui)
```bash
cd /observability-assistant-ui
make install
make dev  # Runs on :3000
```

**Option B: CopilotKit (Development)**
```bash
cd frontend
npm install
npm run dev  # Runs on :8080
```

### 3. MCP Servers (Required)

**Kubernetes MCP Server (port 8001)** - [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server)

```bash
npx kubernetes-mcp-server@latest --port 8001 --kubeconfig ~/.kube/config
```

**Observability MCP Server (port 8002)** - [obs-mcp](https://github.com/rhobs/obs-mcp)

```bash
cd source/obs-mcp
oc login
go run ./cmd/obs-mcp/ --listen 127.0.0.1:8002 --auth-mode kubeconfig --metrics-backend prometheus --insecure
```

**Incident Detection MCP Server (port 8003)** - [cluster-health-analyzer](https://github.com/openshift/cluster-health-analyzer/tree/dev-preview) | [Setup guide](https://developers.redhat.com/articles/2025/10/09/integrate-incident-detection-openshift-lightspeed-mcp)

```bash
oc port-forward -n openshift-cluster-observability-operator svc/cluster-health-mcp-server 8003:8085
```

**Insights Results MCP Server (port 8004)** - [insights-results-mcp](https://github.com/RedHatInsights/insights-results-mcp)

```bash
oc port-forward -n insights-results-mcp svc/insights-results-mcp-server 8004:5000
```

## Features

✅ Natural language cluster queries
✅ Interactive Prometheus metrics charts
✅ Pod logs streaming and viewing
✅ Cluster health incident analysis
✅ Red Hat Insights recommendations
✅ Official OpenShift documentation search
✅ Multi-agent orchestration with specialized expertise
✅ Real-time SSE streaming responses

## Project Structure

```
adk-openshift-agent/
├── backend/                          # Python ADK multi-agent system
│   ├── agent/
│   │   ├── agent.py                 # Router agent
│   │   ├── kubernetes_agent.py      # Cluster operations
│   │   ├── metrics_agent.py         # Prometheus/Thanos
│   │   ├── incident_detection_agent.py  # Health analysis
│   │   ├── insights_agent.py        # Red Hat Insights
│   │   └── openshift_docs_agent.py  # Documentation search
│   ├── main.py                       # FastAPI + AG-UI
│   └── config.py
├── frontend/                         # Next.js + CopilotKit (development)
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Google ADK, LiteLLM, AG-UI
- **Frontend (PatternFly)**: React, Vite, PatternFly 6, Victory.js
- **Frontend (CopilotKit)**: Next.js, CopilotKit, @ag-ui/client
- **LLMs**: OpenAI GPT-4 (main agents), Google Gemini (docs search)
- **Protocol**: AG-UI for agent-UI communication

## External Resources

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [AG-UI Protocol](https://docs.ag-ui.com/)
- [kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server)
- [PatternFly Chatbot](https://www.patternfly.org/patternfly-ai/chatbot/overview/)
- [CopilotKit](https://www.copilotkit.ai/)
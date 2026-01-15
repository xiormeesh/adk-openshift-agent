# Project goal

An agentic chatbot to answer questions about Openshift and help troubleshoot an Openshift cluster connecting to its observability data (metrics, alerts, logs, traces, events) as well as provide information and evaluation of the cluster's health status

# Phases

The purpose of phases is to add features incrementally confirming the previous stage is working before adding more complexity.

## Phase 1 - Done

Using ADK create a basic agent that can answer questions sending the request to an OpenAI model. It should have 
- in memory session management to allow multi-turn queries
- a clear way to test the agent via both curl (API) and `adk web` for development purposes
- backend is running on localhost:8000

### Verify

this must return a valid response from an LLM model (prerequisite FastAPI server must be running):

curl -X POST http://localhost:8000/copilotkit \
    -H "Content-Type: application/json" \
    -d '{"messages": [{"role": "user", "content": "what is kubectl?"}]}'

or 

alternatively `poetry run adk web --port 9999` starts ADK web interface that does not require a running FastAPI server.

## Phase 2 - Done

Adding integration with AG-UI and CopilotKit, showing basic chatbot interface with an input field and a scrollable chat history.
- frontend is running on localhost:8080
- no complicated UI, just basic chatbot interface with an input field and a canvas to put question and answer to

## Phase 3

Adding kubernetes-mcp-server integration
- it's expected to be running on localhost:8001

## Phase 4

Adding obs-mcp integration
- it's expected to be runing on localhost:8002
- agent can query obs-mcp MCP server to query Prometheus for metrics the user requests

## final phase

Adding proper multi-agent architecture with a Router agent that delegates work to specific agents with their own tools provided by the MCP servers
- Openshift knowledge and documentation expert capable of looking up openshift documentation using built-inweb search
- Openshift troubleshooting expert that knows best practices for troubleshooting Kubernetes clusters (checking cluster health overview and existing alerts) and can delegate to specific data sources experts
- Openshift metrics expert
- Openshift logging expert
- Openshift tracing expert

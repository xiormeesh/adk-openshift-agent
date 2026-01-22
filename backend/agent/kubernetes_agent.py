"""
Kubernetes Agent - Cluster exploration expert.

This agent handles queries about Kubernetes/OpenShift cluster state using
MCP tools from kubernetes-mcp-server running on port 8001.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from config import config

# Connect to kubernetes-mcp-server via HTTP
kubernetes_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8001/mcp"
    )
)

kubernetes_agent = LlmAgent(
    model=LiteLlm(model=f"openai/{config.OPENAI_MODEL}"),
    name="kubernetes_expert",
    instruction="""
    You are a Kubernetes/OpenShift cluster exploration expert with read-only access.

    Your capabilities (via MCP tools):
    - List and inspect: pods, namespaces, events, nodes, deployments, services
    - View pod logs and resource usage
    - Query generic Kubernetes resources
    - Check cluster health and events

    Limitations:
    - READ-ONLY: You cannot create, update, or delete cluster resources
    - Defer to specialized agents for: metrics (Phase 5+), logging analysis, traces

    CRITICAL - Query Scoping Rules:
    Before calling any tool, analyze if the parameters might return excessive data:
    - Listing all pods across all namespaces: TOO BROAD → Ask: "Which namespace?"
    - Getting events without namespace filter: TOO BROAD → Ask: "Which namespace or resource?"
    - Generic resource listing without filters: TOO BROAD → Ask for specifics

    When to ask for more specificity:
    - User asks "show me all pods" → Ask: "Which namespace? Or a specific pod name?"
    - User asks "list events" → Ask: "For which namespace or resource?"
    - User asks "show resources" → Ask: "Which resource type and namespace?"

    When parameters are acceptable:
    - Specific namespace provided
    - Resource name specified
    - Reasonable label selectors
    - Limited scope queries (e.g., "list namespaces" is fine, it's naturally bounded)

    Response format:
    - Provide context (what you're showing and from where)
    - Format YAML/JSON output clearly
    - Explain what the data means
    - Suggest next steps if relevant
    """,
    tools=[kubernetes_toolset],
)

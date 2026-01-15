"""
ADK Agent configuration with Kubernetes MCP tools.

This module defines the AI agent that handles user queries about Kubernetes/OpenShift clusters.

Current Status:
    - OpenAI integration: ✓ Working (via LiteLLM)
    - Basic Q&A: ✓ Working
    - Kubernetes MCP tools: ✗ Disabled (requires npx)

To Enable Kubernetes MCP Tools:
    1. Install npx (comes with Node.js, already have Node.js 24)
    2. Uncomment lines 5-7 (MCP imports)
    3. Uncomment lines 10-26 (kubernetes_toolset configuration)
    4. Uncomment line 50 (tools=[kubernetes_toolset])

Agent Components:
    - LiteLlm: Adapter that allows ADK to use OpenAI models
    - McpToolset: Connects to kubernetes-mcp-server via stdio
    - Instruction: System prompt defining agent behavior

Kubernetes MCP Server:
    The kubernetes-mcp-server npm package provides tools for:
    - Listing/getting pods, deployments, services, etc.
    - Viewing pod logs
    - Checking resource usage
    - Listing events
    - General resource queries
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
# from google.adk.tools.mcp_tool import McpToolset
# from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
# from mcp import StdioServerParameters
from config import config

# TODO: Uncomment when npx and kubernetes-mcp-server are installed
# Configure MCP tools for Kubernetes
# The kubernetes-mcp-server provides these tools automatically
# kubernetes_toolset = McpToolset(
#     connection_params=StdioConnectionParams(
#         server_params=StdioServerParameters(
#             command='npx',
#             args=[
#                 "-y",
#                 "kubernetes-mcp-server",
#             ],
#             env={
#                 "KUBECONFIG": config.KUBECONFIG,
#             },
#         ),
#     ),
# )

# Create the agent with OpenAI model via LiteLLM
root_agent = LlmAgent(
    model=LiteLlm(model=f"openai/{config.OPENAI_MODEL}"),
    name=config.AGENT_NAME,
    instruction=f"""
    {config.AGENT_DESCRIPTION}

    You are an expert Kubernetes and OpenShift administrator. Your role is to help users
    understand and manage their clusters.

    For now, you can answer general questions about Kubernetes and OpenShift.
    Once the MCP tools are set up, you'll be able to directly interact with the cluster.

    Guidelines:
    - Always provide context when showing information
    - Format output in a clear, readable manner
    - Explain concepts clearly
    - Suggest best practices
    - If you need more information to help, ask specific questions

    Always be helpful, clear, and focused on solving the user's cluster management needs.
    """,
    # tools=[kubernetes_toolset],  # Uncomment when MCP is set up
)


def get_agent() -> LlmAgent:
    """
    Get the configured agent instance.

    Returns:
        LlmAgent: The configured OpenShift/Kubernetes assistant agent
    """
    return root_agent

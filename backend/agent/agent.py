"""
ADK Agent configuration - Multi-agent architecture (Phase 4).

This module defines the router agent that orchestrates specialized sub-agents.

Architecture Pattern: Agent-as-Tool
    - Router agent delegates to specialized agents (Kubernetes, Metrics, etc.)
    - Uses AgentTool wrapper to expose sub-agents as callable tools
    - LLM decides when to invoke specialized agents
    - Automatic state and artifact synchronization

Current Sub-Agents:
    - Kubernetes Agent: Cluster exploration expert (currently in stub mode)
    - Future: Metrics Agent, Logging Agent, Documentation Agent

Current Status:
    - Router agent: ✓ Working
    - Kubernetes delegation: ✓ Working (stub mode)
    - Multi-agent architecture: ✓ Active

Next Steps:
    - Enable MCP tools in kubernetes_agent.py
    - Add more specialized agents (metrics, logging, docs)
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import AgentTool
from config import config
from .kubernetes_agent import kubernetes_agent


# Wrap the kubernetes_agent as a tool using AgentTool
# The AgentTool wrapper automatically handles:
# - Execution of the agent when the LLM calls this tool
# - State and artifact synchronization back to parent context
# - Proper return value formatting
# Note: AgentTool uses the agent's name and instruction as tool metadata
kubernetes_tool = AgentTool(agent=kubernetes_agent)


# Router agent - orchestrates all specialized agents
root_agent = LlmAgent(
    model=LiteLlm(model=f"openai/{config.OPENAI_MODEL}"),
    name="openshift_router",
    instruction="""
You are the orchestrator for an OpenShift/Kubernetes AI assistant system.

Your responsibilities:
1. Analyze user queries to determine which specialized agent should handle them
2. Delegate cluster exploration queries to the Kubernetes Agent
3. Relay responses back to the user clearly and concisely
4. If a query spans multiple domains, coordinate between agents

Current available agents:
- Kubernetes Agent: Cluster state exploration (pods, namespaces, events, resources, logs)
- More agents coming in future phases (metrics, logging, documentation)

Guidelines:
- Always relay agent responses without modification unless clarification is needed
- If unsure which agent to use, ask the user for clarification
- Keep responses focused and actionable
- For general Kubernetes/OpenShift questions that don't require cluster access, you can answer directly

When to delegate to Kubernetes Agent:
- User asks about specific resources in their cluster
- User wants to see logs, events, or resource usage
- User needs to inspect cluster state
- User asks "what pods are running", "show me namespaces", etc.

When to answer directly:
- General Kubernetes/OpenShift concepts
- Best practices and recommendations
- Documentation questions
- "How do I..." questions that don't require cluster inspection
""",
    tools=[kubernetes_tool],
)


def get_agent() -> LlmAgent:
    """
    Get the configured agent instance.

    Returns:
        LlmAgent: The router agent (multi-agent orchestrator)
    """
    return root_agent

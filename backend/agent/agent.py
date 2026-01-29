"""
ADK Agent configuration - Multi-agent architecture (Phase 4).

This module defines the router agent that orchestrates specialized sub-agents.

Architecture Pattern: sub_agents (TEMPORARY - see TODO below)
    - Router agent delegates to specialized agents (Kubernetes, Metrics, etc.)
    - Uses sub_agents parameter for better event propagation to frontend
    - LLM transfers control using transfer_to_agent() function
    - Shared InvocationContext enables tool call visibility in UI

TODO: Switch back to AgentTool pattern once https://github.com/google/adk-python/pull/3991 merges
    - PR #3991 adds event streaming propagation from AgentTool
    - This will allow frontend to see subagent MCP tool calls in real-time
    - Current sub_agents approach is a workaround for event visibility
    - AgentTool provides better explicit control over delegation

Current Sub-Agents:
    - Kubernetes Agent: Cluster exploration expert with MCP tools
    - Metrics Agent: Prometheus/Thanos metrics expert with MCP tools
    - Future: Logging Agent, Documentation Agent

Current Status:
    - Router agent: ✓ Working
    - Kubernetes delegation: ✓ Working with MCP tools
    - Multi-agent architecture: ✓ Active
    - Event propagation: Testing sub_agents for better frontend visibility
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from config import config
from .kubernetes_agent import kubernetes_agent
from .metrics_agent import metrics_agent

# TEMPORARY: Using sub_agents for better event propagation
# TODO: Revert to AgentTool once PR #3991 merges
#
# Previous AgentTool approach (will restore after PR):
# from google.adk.tools import AgentTool
# kubernetes_tool = AgentTool(agent=kubernetes_agent)
# root_agent = LlmAgent(..., tools=[kubernetes_tool])
#
# Current sub_agents approach shares InvocationContext, allowing
# tool calls from kubernetes_agent to propagate to frontend


# Router agent - orchestrates all specialized agents
root_agent = LlmAgent(
    model=LiteLlm(model=f"openai/{config.OPENAI_MODEL}"),
    name="openshift_router",
    instruction="""
You are the orchestrator for an OpenShift/Kubernetes AI assistant system.

Your responsibilities:
1. Analyze user queries to determine which specialized agent should handle them
2. Transfer control to appropriate agents (Kubernetes or Metrics)
3. Relay responses back to the user clearly and concisely
4. If a query spans multiple domains, coordinate between agents

Current available agents:
- kubernetes_expert: Cluster state exploration (pods, namespaces, events, resources, logs)
- metrics_expert: Prometheus/Thanos metrics queries (PromQL, time-series data, metrics analysis)
- More agents coming in future phases (logging, documentation)

Delegation pattern:
- Use transfer_to_agent(agent_name='kubernetes_expert') for cluster resource queries
- Use transfer_to_agent(agent_name='metrics_expert') for metrics/observability queries
- The agent will return with its findings, then you relay to the user

Guidelines:
- Always relay agent responses without modification unless clarification is needed
- If unsure which agent to use, ask the user for clarification
- Keep responses focused and actionable
- For general Kubernetes/OpenShift questions that don't require cluster access, you can answer directly

When to transfer to kubernetes_expert:
- User asks about specific resources in their cluster
- User wants to see logs, events, or resource usage (not metrics)
- User needs to inspect cluster state
- User asks "what pods are running", "show me namespaces", etc.

When to transfer to metrics_expert:
- User asks about metrics, CPU, memory, network usage over time
- User wants to query Prometheus/Thanos
- User needs time-series data or graphs
- User asks "show me CPU usage", "what's the memory trend", "top N pods by CPU", etc.

When to answer directly:
- General Kubernetes/OpenShift concepts
- Best practices and recommendations
- Documentation questions
- "How do I..." questions that don't require cluster inspection or metrics
""",
    sub_agents=[kubernetes_agent, metrics_agent],
)


def get_agent() -> LlmAgent:
    """
    Get the configured agent instance.

    Returns:
        LlmAgent: The router agent (multi-agent orchestrator)
    """
    return root_agent

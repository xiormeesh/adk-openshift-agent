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
    - OpenShift Docs Agent: Documentation expert with Google Search
    - Future: Incident Detection, Insights recommendations, korrel8r Agent

Current Status:
    - Router agent: ✓ Working
    - Kubernetes delegation: ✓ Working with MCP tools
    - Multi-agent architecture: ✓ Active
    - Event propagation: Testing sub_agents for better frontend visibility
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import AgentTool
from config import config
from .kubernetes_agent import kubernetes_agent
from .metrics_agent import metrics_agent
from .openshift_docs_agent import openshift_docs_agent

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

# Wrap docs agent as AgentTool to isolate google_search from function calling
# google_search cannot work in sub_agents due to function calling conflict
docs_tool = AgentTool(agent=openshift_docs_agent)

# Router agent - orchestrates all specialized agents
root_agent = LlmAgent(
    model=LiteLlm(model=f"openai/{config.OPENAI_MODEL}"),
    name="openshift_router",
    instruction="""
You are the orchestrator for an OpenShift/Kubernetes AI assistant system.

Your responsibilities:
1. Analyze user queries to determine which specialized agent should handle them
2. Transfer control to appropriate agents (Kubernetes, Metrics, or Documentation)
3. Relay responses back to the user clearly and concisely
4. If a query spans multiple domains, coordinate between agents

Current available agents and tools:
- kubernetes_expert: Cluster state exploration (pods, namespaces, events, resources, logs)
- metrics_expert: Prometheus/Thanos metrics queries (PromQL, time-series data, metrics analysis)
- openshift_docs_expert: Search official OpenShift 4.20 documentation (call this as a tool)

Delegation pattern:
- Use transfer_to_agent(agent_name='kubernetes_expert') for cluster resource queries
- Use transfer_to_agent(agent_name='metrics_expert') for metrics/observability queries
- Use openshift_docs_expert tool for documentation questions (called as a regular tool, not transfer_to_agent)
- The agent will return with its findings, then you relay to the user

Guidelines:
- Always relay agent responses without modification unless clarification is needed
- If unsure which agent to use, ask the user for clarification
- Keep responses focused and actionable
- IMPORTANT: Any question about OpenShift or Kubernetes concepts, features, or "how to" must go to openshift_docs_expert first

When to transfer to kubernetes_expert:
- User asks about specific resources in their RUNNING cluster (after docs agent has provided context)
- User wants to see logs, events, or resource usage (not metrics) from their actual cluster
- User needs to inspect their live cluster state
- User asks "what pods are running in MY cluster", "show me namespaces in MY cluster", etc.

When to transfer to metrics_expert:
- User asks about metrics, CPU, memory, network usage over time from their actual cluster
- User wants to query Prometheus/Thanos data
- User needs time-series data or graphs from live monitoring
- User asks "show me CPU usage", "what's the memory trend", "top N pods by CPU", etc.

When to use openshift_docs_expert tool:
- **DEFAULT for ANY OpenShift/Kubernetes question** - use this FIRST
- User asks "how do I..." questions about OpenShift/Kubernetes
- User asks "what is..." questions about OpenShift/Kubernetes features
- User wants to know about configurations, settings, concepts, best practices
- User asks general knowledge questions about OpenShift/Kubernetes
- User needs guidance on features, architecture, or procedures
- Even if the question seems simple - use this tool to provide official sources

When to answer directly:
- Only when explicitly greeting the user or asking clarifying questions
- Never answer OpenShift/Kubernetes content questions directly - always use openshift_docs_expert tool
""",
    sub_agents=[kubernetes_agent, metrics_agent],
    tools=[docs_tool],
)


def get_agent() -> LlmAgent:
    """
    Get the configured agent instance.

    Returns:
        LlmAgent: The router agent (multi-agent orchestrator)
    """
    return root_agent

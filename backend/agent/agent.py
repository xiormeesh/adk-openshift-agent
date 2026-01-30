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
    - Incident Detection Agent: Cluster health incident analysis with MCP tools
    - OpenShift Docs Agent: Documentation expert with Google Search
    - Future: Insights recommendations, korrel8r Agent

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
from .incident_detection_agent import incident_detection_agent

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
2. Transfer control to appropriate agents (Kubernetes, Metrics, Incidents, or Documentation)
3. Relay responses back to the user clearly and concisely
4. If a query spans multiple domains, coordinate between agents

Current available agents and tools:
- kubernetes_expert: Cluster state exploration (pods, namespaces, events, resources, logs)
- metrics_expert: Prometheus/Thanos metrics queries (PromQL, time-series data, metrics analysis)
- incident_detection_expert: Cluster health incidents and root cause analysis
- openshift_docs_expert: Search official OpenShift 4.20 documentation (call this as a tool)

Delegation pattern:
- Use transfer_to_agent(agent_name='kubernetes_expert') for cluster resource queries
- Use transfer_to_agent(agent_name='metrics_expert') for metrics/observability queries
- Use transfer_to_agent(agent_name='incident_detection_expert') for incident analysis
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

When to transfer to incident_detection_expert:
- User asks about incidents or cluster health issues
- User wants to know "what's wrong with my cluster", "are there any issues"
- User asks to analyze specific problems or symptoms
- User wants root cause analysis for cluster problems
- User asks "what incidents are firing", "explain this incident", etc.

SPECIAL CASE - When user asks about alerts:
- Transfer to BOTH metrics_expert AND incident_detection_expert
- First get alerts from metrics_expert (Prometheus firing alerts)
- Then get incidents from incident_detection_expert (detected health issues)
- Combine both responses to give complete picture:
  * metrics_expert provides: Which Prometheus alerts are firing, alert details, metrics
  * incident_detection_expert provides: Detected incidents, root causes, remediation
- Present both alert AND incident information together for comprehensive analysis

When to use openshift_docs_expert tool:
- User asks GENERIC "how do I..." questions about OpenShift/Kubernetes features or procedures
- User asks "what is..." questions about OpenShift/Kubernetes concepts (not cluster state)
- User wants to know about configurations, settings, best practices
- User asks GENERAL KNOWLEDGE questions that don't involve inspecting their cluster
- User needs guidance on features, architecture, or procedures
- Questions like: "how do I configure persistent volumes", "what is an operator", "how do I install X"

IMPORTANT - Do NOT use docs agent for:
- Live cluster investigation: "what alerts are firing", "show me incidents", "what pods are running"
- Troubleshooting active issues: "why is my cluster slow", "what's causing this error"
- Inspecting current state: "what's the CPU usage", "are there any problems"
- These should go to the appropriate cluster investigation agents (metrics, incidents, kubernetes)

When to answer directly:
- Greeting the user or acknowledging their message
- Asking clarifying questions about what they need
- Simple routing explanations ("I'll check the cluster state for you", etc.)
""",
    sub_agents=[kubernetes_agent, metrics_agent, incident_detection_agent],
    tools=[docs_tool],
)


def get_agent() -> LlmAgent:
    """
    Get the configured agent instance.

    Returns:
        LlmAgent: The router agent (multi-agent orchestrator)
    """
    return root_agent

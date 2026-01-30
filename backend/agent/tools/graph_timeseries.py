"""
Graph timeseries data tool - wraps obs-mcp execute_range_query for frontend visualization.

This tool provides a clean interface for graphing Prometheus metrics in the frontend.
It calls obs-mcp's execute_range_query internally and returns data in the format
expected by observability-assistant-ui's TimeSeriesChart component.
"""

from typing import Optional
import json
import httpx


def _extract_text_content(content_items: list) -> str:
    """Extract text from MCP content items."""
    for item in content_items:
        if item.get("type") == "text":
            return item.get("text", "")
    return ""


async def graph_timeseries_data(
    query: str,
    description: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    step: Optional[str] = None,
) -> str:
    """
    Execute a PromQL range query and return time-series data formatted for graphing.

    This tool queries Prometheus/Thanos and returns data in a format that the frontend
    can render as an interactive time-series chart.

    Args:
        query: PromQL query to execute
        description: Human-readable description of what this graph shows
        start: Start time (ISO8601 or relative like "NOW-1h", default: NOW-1h)
        end: End time (ISO8601 or relative like "NOW", default: NOW)
        step: Query resolution step (e.g., "5m", default: auto-calculated)

    Returns:
        JSON string with graph data in format:
        {
            "query": "...",
            "description": "...",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {"label": "value", ...},
                        "values": [[timestamp, "value"], ...]
                    }
                ]
            }
        }
    """
    # Build MCP request payload for execute_range_query tool
    # Provide defaults for required/recommended parameters
    mcp_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "execute_range_query",
            "arguments": {
                "query": query,
                "start": start or "NOW-1h",  # Default to last hour
                "end": end or "NOW",
                "step": step or "1m",  # Required by obs-mcp
            }
        }
    }

    # Call obs-mcp-server directly via HTTP
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8002/mcp",
                json=mcp_request,
            )
            response.raise_for_status()

            # Parse MCP response
            mcp_response = response.json()

            if "error" in mcp_response:
                return json.dumps({
                    "error": f"MCP error: {mcp_response['error']}",
                    "query": query,
                    "description": description,
                })

            # Extract tool result from MCP response
            # MCP returns: { result: { content: [{ type: "text", text: "..." }] } }
            tool_result = mcp_response.get("result", {})

            # Check if MCP server returned an error
            if tool_result.get("isError"):
                error_msg = _extract_text_content(tool_result.get("content", [])) or "Unknown error"
                return json.dumps({
                    "error": f"Query failed: {error_msg}",
                    "query": query,
                    "description": description,
                })

            # Extract and parse the Prometheus data from MCP response
            text_content = _extract_text_content(tool_result.get("content", []))
            if not text_content:
                return json.dumps({
                    "error": "No data returned from query",
                    "query": query,
                    "description": description,
                })

            try:
                prometheus_data = json.loads(text_content)
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": f"Failed to parse response: {str(e)}",
                    "query": query,
                    "description": description,
                })

            # Format for frontend
            graph_data = {
                "query": query,
                "description": description,
                "data": prometheus_data,  # Should be { resultType: 'matrix', result: [...] }
            }

            return json.dumps(graph_data)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to execute query: {str(e)}",
            "query": query,
            "description": description,
        })

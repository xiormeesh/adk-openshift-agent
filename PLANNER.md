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

## Phase 3 - Done

Make ADK backend compatible with observability-assistant-ui (PatternFly-based frontend running separately).

### Overview

The observability-assistant-ui is a separate application (running on http://localhost:3000) built with PatternFly components. Our goal is to make our ADK backend compatible with it so it can replace the CopilotKit frontend.

**Important:**
- observability-assistant-ui runs **separately** (not part of this repo)
- `source/` folder contains reference code for analyzing implementation patterns
- Backend stays on :8000, frontend on :3000
- MCP servers will use :8001, :8002, :8003, etc.

### Port Allocation

- **:3000** - observability-assistant-ui (external, PatternFly frontend)
- **:8000** - ADK backend (this project)
- **:8001** - kubernetes-mcp-server (Phase 4)
- **:8002** - obs-mcp server (Phase 5)
- **:8003+** - Additional MCP servers as needed

### Frontend Architecture (Reference)

**observability-assistant-ui** (external application):
- Built with PatternFly 6 + @patternfly/chatbot
- React 18 + TypeScript + Vite
- Supports ag-ui protocol via SSE streaming
- Features: Prometheus charts, tool call visualization, step progress, markdown rendering

**ag-ui Protocol Contract:**
- **Endpoint:** Expects backend at `/api/chat` (configurable via proxy)
- **Request:** POST with RunAgentInput (threadId, runId, messages, state, tools, context, forwardedProps)
- **Response:** SSE stream of ag-ui events (RUN_STARTED, TEXT_MESSAGE_*, TOOL_CALL_*, STEP_*, RUN_ERROR)

### Backend Requirements

Make ADK backend compatible by:

1. **Verify ag-ui protocol compatibility**
   - Check if `add_adk_fastapi_endpoint()` creates compatible endpoints
   - Verify SSE event format matches observability-assistant-ui expectations
   - Test with actual frontend running on :3000

2. **Configure CORS**
   - Add http://localhost:3000 to allowed origins
   - Ensure SSE streaming works cross-origin

3. **Endpoint mapping options**
   - **Option A:** Verify existing endpoints work with frontend proxy
   - **Option B:** Add `/api/chat` endpoint if needed
   - **Option C:** Document correct proxy configuration for frontend

### Tasks

1. **Backend Compatibility**
   - [x] Update CORS_ORIGINS to include http://localhost:3000
   - [x] Test if existing `add_adk_fastapi_endpoint()` works with observability-assistant-ui
   - [x] Document exact endpoint paths and formats
   - [x] Verify ag-ui event streaming format

2. **Integration Testing**
   - [x] Configure observability-assistant-ui to point to :8000
   - [x] Test basic chat messages
   - [x] Verify streaming text works correctly
   - [x] Error handling verified (RUN_ERROR events supported)

3. **Documentation**
   - [x] Document how to run observability-assistant-ui with this backend
   - [x] Update README.md with integration instructions
   - [x] Document ag-ui protocol implementation details (AG_UI_PROTOCOL.md)

4. **Cleanup**
   - [x] Keep both frontends (CopilotKit as development reference)
   - [x] Update main README to document both frontends
   - [x] Backend ready for multi-agent architecture (Phase 4+)

### Integration Approach

**Step 1:** Research
- Analyze `source/observability-assistant-ui/` code to understand exact requirements
- Document ag-ui event format from types/agui.ts
- Verify what `add_adk_fastapi_endpoint()` actually provides

**Step 2:** Backend adjustments
- Update CORS configuration
- Add any missing endpoints or event formats
- Ensure SSE streaming works correctly

**Step 3:** Frontend configuration
- Configure observability-assistant-ui proxy to point to :8000
- Test demo mode first
- Test with live backend

**Step 4:** Verification
- End-to-end testing of chat functionality
- Verify tool calls render when MCP servers added (Phase 4+)
- Confirm step progress indicators work

### Important Notes

- **holmesGPT reference only**: observability-assistant-ui was built for holmesGPT, we use ADK
- **ag-ui is the common protocol**: Both systems use ag-ui for compatibility
- **PatternFly provides OpenShift-aligned UI**: Essential for production deployment
- **Keep both frontends temporarily**: Until fully verified

### Resources

- Reference code: `source/observability-assistant-ui/`
- PatternFly Chatbot: https://www.patternfly.org/patternfly-ai/chatbot/overview/
- PatternFly GitHub: https://github.com/patternfly/chatbot
- ag-ui Protocol: https://github.com/ag-ui-protocol/ag-ui
- holmesGPT (reference): https://github.com/robusta-dev/holmesgpt and `source/holmesgpt/`

### Success Criteria

Phase 3 complete when:
1. ✅ Backend CORS configured for :3000
2. ✅ observability-assistant-ui (running on :3000) successfully connects to backend (:8000)
3. ✅ Chat messages stream correctly with markdown rendering
4. ✅ Error messages display as PatternFly alerts (RUN_ERROR event support verified)
5. ✅ Ready to add tool calls in Phase 4 (will test with observability-assistant-ui)
6. ✅ Documentation updated for running both applications

**Deliverables:**
- AG_UI_PROTOCOL.md: Complete AG-UI endpoint documentation
- PLAYWRIGHT.md: Frontend testing guide
- README.md: Updated with both frontend options
- Both frontends tested and working

## Phase 4 - Kubernetes MCP Integration

**Goal:** Add multi-agent architecture with Router agent and Kubernetes expert subagent using kubernetes-mcp-server tools.

**Reference:** Documentation, READMEs, and source code for kubernetes-mcp-server are available in `source/kubernetes-mcp-server/`

### Overview

Create a two-agent system:
1. **Router Agent** - Main orchestrator that delegates to specialized agents
2. **Kubernetes Agent** - Cluster exploration expert with MCP tools from kubernetes-mcp-server (port 8001)

### Architecture

```
User Request → Router Agent → Kubernetes Agent (MCP Tools) → kubernetes-mcp-server:8001
                     ↓                    ↓
                 Response ←────────────────┘
```

**Key Principles:**
- Tool discovery is **dynamic** (MCP server provides tool list)
- Kubernetes agent is **read-only** (can query but not modify cluster)
- Smart query scoping (reject overly broad queries)
- Router delegates based on query domain

### Agent Specifications

#### 1. Router Agent (Orchestrator)

**File:** `backend/agent/router_agent.py`

**Responsibilities:**
- Receive user queries
- Determine which specialized agent(s) to call
- Relay responses to user
- Future: Coordinate human-in-the-loop interactions

**System Prompt Guidelines:**
```
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
```

**Tools:**
- `delegate_to_kubernetes` - Calls Kubernetes Agent with user query

#### 2. Kubernetes Agent (Cluster Expert)

**File:** `backend/agent/kubernetes_agent.py`

**Responsibilities:**
- Answer questions about cluster state
- Query resources via MCP tools
- Intelligently scope queries to avoid overwhelming data
- Provide read-only cluster information

**System Prompt Guidelines:**
```
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
```

**MCP Connection:**
- Server: kubernetes-mcp-server on localhost:8001
- Protocol: MCP via stdio or HTTP
- Tools: Dynamically discovered from MCP server

**Available Tool Categories** (dynamic, reference only):
- Events: `events_list`
- Namespaces: `namespaces_list`, `projects_list`
- Pods: `pods_list`, `pods_get`, `pods_log`, `pods_top`
- Nodes: `nodes_top`, `nodes_log`, `nodes_stats_summary`
- Resources: `resources_list`, `resources_get`
- Helm: `helm_list`

### Implementation Plan

**Assumption:** kubernetes-mcp-server is running on localhost:8001 (no authentication required for development).

#### Step 1: Create Kubernetes Agent
**File:** `backend/agent/kubernetes_agent.py` (new)

- Create LlmAgent with kubernetes_expert name
- Add McpToolset connecting to kubernetes-mcp-server via stdio
- Use StdioConnectionParams with npx command to spawn MCP server
- Configure with KUBECONFIG environment variable
- Set system prompt from Agent Specifications above

#### Step 2: Create Router Agent
**File:** `backend/agent/router_agent.py` (new)

- Create LlmAgent with openshift_router name
- Define `delegate_to_kubernetes_agent` tool function
- Tool calls kubernetes_agent.process(query) and returns result
- Add delegation tool to router agent's toolset
- Set system prompt from Agent Specifications above

#### Step 3: Update Main Entry Point
**File:** `backend/agent/agent.py`

- Import router_agent and expose it as root_agent
- Update get_agent() to return router_agent

#### Step 4: Configuration Updates
**File:** `backend/config.py`

- Add KUBECONFIG setting (default ~/.kube/config)
- Add MCP server port configuration if needed

### Testing Strategy

#### Unit Tests

**File:** `backend/tests/test_kubernetes_agent.py` (new)

Test scenarios:
1. Agent initialization with MCP tools
2. Tool discovery from MCP server
3. Query scoping logic (reject overly broad queries)
4. Successful tool execution with good parameters
5. Error handling for failed MCP calls

#### Integration Tests

**File:** `backend/tests/test_router_kubernetes.py` (new)

Test scenarios:
1. Router → Kubernetes agent delegation
2. End-to-end cluster query flow
3. Response formatting and relay
4. Multiple agent calls in sequence

#### Manual Testing Checklist

**Prerequisites:**
- [x] kubernetes-mcp-server running on :8001
- [x] Backend running on :8000
- [x] Kubeconfig with valid cluster access

**Test Cases:**

1. **Basic Delegation**
   - Query: "What namespaces exist in the cluster?"
   - Expected: Router delegates to K8s agent, returns namespace list
   - Frontend: Both :3000 and :8080

2. **Query Scoping - Too Broad**
   - Query: "Show me all pods"
   - Expected: K8s agent asks "Which namespace?"
   - Verify response is helpful, not error

3. **Query Scoping - Acceptable**
   - Query: "Show me pods in the default namespace"
   - Expected: Returns pod list with clear formatting

4. **Events Query**
   - Query: "What cluster events happened recently?"
   - Expected: May ask for namespace, or show cluster-wide events
   - Verify YAML formatting is readable

5. **Pod Logs**
   - Query: "Show logs for pod <name> in namespace <ns>"
   - Expected: Returns log output clearly formatted

6. **Resource Usage**
   - Query: "Show me node resource usage"
   - Expected: Calls `nodes_top`, returns CPU/memory stats

7. **Unknown Domain**
   - Query: "What's the weather today?"
   - Expected: Router indicates no appropriate agent available

8. **Tool Calling Visibility**
   - Verify frontend shows tool calls being executed
   - PatternFly: Check tool visualization
   - CopilotKit: Check tool display

#### Frontend Testing

**PatternFly UI (:3000):**
- [x] Tool calls render in collapsed sections
- [x] Tool arguments shown
- [x] Tool results displayed
- [ ] Steps indicator works (if agent uses steps)
- [ ] Errors display as PatternFly alerts

**CopilotKit UI (:8080):**
- [ ] Tool calls visible in chat
- [ ] Results formatted clearly

### Success Criteria

Phase 4 complete when:

1. **Architecture**
   - ✅ Router agent properly delegates to Kubernetes agent
   - ✅ Kubernetes agent has dynamic MCP tools from kubernetes-mcp-server
   - ✅ Multi-agent system works end-to-end

2. **Functionality**
   - ✅ Can query: namespaces, pods, events, nodes, resources
   - ✅ Query scoping prevents overly broad queries
   - ✅ Tool calls execute successfully through MCP
   - ✅ Responses are clear and well-formatted

3. **Testing**
   - ✅ All manual test cases pass
   - ✅ Both frontends work with new multi-agent system
   - ✅ Tool visualization works in both frontends

4. **Documentation**
   - ✅ MCP server setup documented
   - ✅ Agent architecture documented
   - ✅ Testing guide created
   - ✅ README updated with Phase 4 status

### Known Limitations

- **Read-only:** Cannot create/modify/delete cluster resources
- **No metrics yet:** Prometheus queries come in Phase 5
- **No planning:** Human-in-the-loop comes in Phase 7
- **Simple delegation:** Router uses basic tool-based delegation (hierarchical agents in final phase)

### Troubleshooting

**Issue:** MCP server not starting
- Check: npx installed (`npx --version`)
- Check: kubernetes-mcp-server version (`npx -y kubernetes-mcp-server@latest --version`)
- Check: Port 8001 available (`lsof -i :8001`)

**Testing MCP server directly:**

Test in **inspector mode (STDIO)** for interactive debugging:
```bash
npx -y @modelcontextprotocol/inspector npx kubernetes-mcp-server@latest --kubeconfig /var/lib/miniagent/kubeconfig
```
This launches an interactive inspector UI to test MCP tools and see request/response flow.

Test in **HTTP streaming mode** (production):
```bash
npx kubernetes-mcp-server@latest --port 8001 --kubeconfig /var/lib/miniagent/kubeconfig
```
This runs the MCP server in HTTP mode on port 8001 for backend integration.

**Issue:** Agent can't connect to MCP server
- Verify: MCP server running and healthy
- Check logs: Backend should show MCP connection attempts
- Test: `curl http://localhost:8001/health`

**Issue:** "Too broad" logic too aggressive
- Adjust: Kubernetes agent system prompt
- Tune: Add examples of acceptable queries
- Test: Iterate on prompt wording

**Issue:** Tool calls not showing in frontend
- Verify: AG-UI TOOL_CALL_* events being sent
- Check: Browser console for `[AG-UI] IN:` logs
- Test: Both frontends behave differently (PatternFly vs CopilotKit)

### Next Steps (Phase 5)

After Phase 4 is complete:
- Add obs-mcp server for Prometheus metrics (:8002)
- Create Metrics Agent with obs-mcp tools
- Implement Prometheus chart rendering in frontends
- Router delegates metrics queries to Metrics Agent

## Phase 5

Adding obs-mcp integration
- it's expected to be runing on localhost:8002
- agent can query metrics using tools provided by obs-mcp server
- frontend can graph prometheus timeseries data returned by the tools (check graph_timeseries_data and kubernetes_tabular_query for inspiration)

## Phase 6

Adding Openshift documentation agent

## Phase 7

Adding planning mode and human in the loop

## final phase

Adding proper multi-agent architecture with a Router agent that delegates work to specific agents with their own tools provided by the MCP servers
- Openshift knowledge and documentation expert capable of looking up openshift documentation using built-inweb search
- Openshift troubleshooting expert that knows best practices for troubleshooting Kubernetes clusters (checking cluster health overview and existing alerts) and can delegate to specific data sources experts
- Openshift metrics expert
- Openshift logging expert
- Openshift tracing expert


### Future Optimization (Post-PoC)

**TODO: Simplify CopilotKit frontend to connect directly to backend**

Current architecture uses a Next.js API route as a proxy:
```
Browser → /api/copilotkit (Next.js) → HttpAgent → Backend (/api/chat)
```

Potential simplification (like PatternFly does):
```
Browser → Backend (/api/chat) directly
```

**Investigation needed:**
- Test if CopilotKit can use `runtimeUrl="http://localhost:8000/api/chat"` directly
- Known issue: CopilotKit sometimes has compatibility issues with FastAPI backends
- GitHub issue: https://github.com/CopilotKit/CopilotKit/issues/1907
- If it works, we can remove the Next.js API route entirely

**Priority:** Low - Current proxy approach works fine for PoC

---

**TODO: Evaluate using @ag-ui/client and @ag-ui/core libraries**

The observability-assistant-ui currently implements the ag-ui protocol manually (~500 lines in `useAgUiStream.ts`), while the CopilotKit frontend uses the official `@ag-ui/client` library (~10 lines).

**Potential investigation:**
- Can `@ag-ui/client` support PatternFly's custom content blocks pattern (interleaved text/steps/tools)?
- Would using the official library reduce maintenance burden without sacrificing functionality?
- Does PatternFly integration require the custom implementation, or can they work together?

**Priority:** Low - PoC functionality comes first. Only investigate if maintenance becomes an issue or if ag-ui library adds features we need.

---

**TODO: Add proper logging/tracing for agent flow**

Current state: Basic ADK DEBUG logging to `adk_debug.log` shows LiteLLM requests/responses and tool invocations.

**Potential improvements:**
- Custom structured logging showing agent → subagent → tool call hierarchy
- Visual nesting with arrows (e.g., `-> router → --> kubernetes_agent → ---> pods_list()`)
- Truncated responses (full arguments, 50-char responses)
- Integration with observability tools (OpenTelemetry, etc.)

**Priority:** Very Low - Current ADK DEBUG logging is likely sufficient for PoC. Only implement if debugging multi-agent flow becomes difficult.
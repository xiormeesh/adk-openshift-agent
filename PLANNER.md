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

## Phase 3 - In Progress

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
   - [ ] Update CORS_ORIGINS to include http://localhost:3000
   - [ ] Test if existing `add_adk_fastapi_endpoint()` works with observability-assistant-ui
   - [ ] Document exact endpoint paths and formats
   - [ ] Verify ag-ui event streaming format

2. **Integration Testing**
   - [ ] Configure observability-assistant-ui to point to :8000
   - [ ] Test basic chat messages
   - [ ] Verify streaming text works correctly
   - [ ] Test error handling

3. **Documentation**
   - [ ] Document how to run observability-assistant-ui with this backend
   - [ ] Update README.md with integration instructions
   - [ ] Document ag-ui protocol implementation details

4. **Cleanup (if successful)**
   - [ ] Consider deprecating CopilotKit frontend (keep for reference initially)
   - [ ] Update main README to recommend observability-assistant-ui
   - [ ] Focus backend development on multi-agent architecture

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
1. Backend CORS configured for :3000
2. observability-assistant-ui (running on :3000) successfully connects to backend (:8000)
3. Chat messages stream correctly with markdown rendering
4. Error messages display as PatternFly alerts
5. Ready to add tool calls in Phase 4 (will test with observability-assistant-ui)
6. Documentation updated for running both applications

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
## Phase 4

Adding kubernetes-mcp-server integration
- it's expected to be running on localhost:8001

## Phase 5

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

# AG-UI Protocol Implementation

This document describes the AG-UI protocol endpoints exposed by the ADK backend and how frontends connect to them.

## Overview

The backend uses `add_adk_fastapi_endpoint()` from the `ag-ui-adk` library to automatically expose AG-UI protocol endpoints. This enables real-time streaming communication between the frontend and the ADK agent.

## Backend Endpoints

### Health Checks

#### `GET /`
Basic health check.

**Response:**
```json
{
  "status": "ok",
  "agent": "openshift_assistant",
  "version": "0.1.0"
}
```

#### `GET /health`
Detailed health check with configuration.

**Response:**
```json
{
  "status": "healthy",
  "agent": "openshift_assistant",
  "model": "gpt-4-turbo-preview",
  "ag_ui": "enabled"
}
```

### AG-UI Endpoint

#### `POST /api/chat`
Main AG-UI protocol endpoint for agent interaction.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body (RunAgentInput):**
```json
{
  "threadId": "thread-1234567890",
  "runId": "run-1234567890",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "what is the latest OpenShift version?"
    }
  ],
  "state": {},
  "tools": [],
  "context": [],
  "forwardedProps": {}
}
```

**Response:**
Server-Sent Events (SSE) stream with `Content-Type: text/event-stream`

**SSE Event Types:**

1. **RUN_STARTED** - Agent run begins
```json
{
  "type": "RUN_STARTED",
  "threadId": "thread-1234567890",
  "runId": "run-1234567890"
}
```

2. **TEXT_MESSAGE_START** - Assistant message begins
```json
{
  "type": "TEXT_MESSAGE_START",
  "messageId": "71e1bf74-f446-4bce-9f4e-bcf0a6c22e51",
  "role": "assistant"
}
```

3. **TEXT_MESSAGE_CONTENT** - Streaming text content (character by character)
```json
{
  "type": "TEXT_MESSAGE_CONTENT",
  "messageId": "71e1bf74-f446-4bce-9f4e-bcf0a6c22e51",
  "contentDelta": "A"
}
```

4. **TEXT_MESSAGE_END** - Message streaming complete
```json
{
  "type": "TEXT_MESSAGE_END",
  "messageId": "71e1bf74-f446-4bce-9f4e-bcf0a6c22e51"
}
```

5. **TOOL_CALL_START** - Tool invocation begins (Phase 4+)
```json
{
  "type": "TOOL_CALL_START",
  "toolCallId": "call-123",
  "name": "get_pods"
}
```

6. **TOOL_CALL_ARGS_CONTENT** - Tool arguments streaming
```json
{
  "type": "TOOL_CALL_ARGS_CONTENT",
  "toolCallId": "call-123",
  "argsDelta": "{\"namespace\":"
}
```

7. **TOOL_CALL_ARGS_DONE** - Tool arguments complete
```json
{
  "type": "TOOL_CALL_ARGS_DONE",
  "toolCallId": "call-123"
}
```

8. **TOOL_CALL_RESULT** - Tool execution result
```json
{
  "type": "TOOL_CALL_RESULT",
  "toolCallId": "call-123",
  "result": "{\"pods\": [...]}"
}
```

9. **TOOL_CALL_DONE** - Tool call complete
```json
{
  "type": "TOOL_CALL_DONE",
  "toolCallId": "call-123"
}
```

10. **STEP_START** - Agent step begins
```json
{
  "type": "STEP_START",
  "stepId": "step-1",
  "name": "Analyzing cluster state"
}
```

11. **STEP_DONE** - Agent step complete
```json
{
  "type": "STEP_DONE",
  "stepId": "step-1"
}
```

12. **RUN_ERROR** - Error occurred during run
```json
{
  "type": "RUN_ERROR",
  "error": {
    "title": "Error",
    "body": "Failed to connect to OpenAI API"
  }
}
```

13. **STATE_SNAPSHOT** - Current state snapshot
```json
{
  "type": "STATE_SNAPSHOT",
  "snapshot": {
    "_ag_ui_thread_id": "thread-1234567890",
    "_ag_ui_run_id": "run-1234567890"
  }
}
```

14. **RUN_FINISHED** - Agent run complete
```json
{
  "type": "RUN_FINISHED",
  "threadId": "thread-1234567890",
  "runId": "run-1234567890"
}
```

## Frontend Integration

### PatternFly Frontend (Port 3000)

**Configuration:** `source/observability-assistant-ui/vite.config.ts`
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

**Connection:**
- Frontend makes requests to `/api/chat` (proxied to backend)
- Custom SSE streaming implementation in `useAgUiStream.ts`
- Handles all AG-UI events for rendering in PatternFly UI

### CopilotKit Frontend (Port 8080)

**Configuration:** `frontend/app/api/copilotkit/route.ts`
```typescript
const runtime = new CopilotRuntime({
  agents: {
    openshift_assistant: new HttpAgent({
      url: `${BACKEND_URL}/api/chat`
    }),
  },
});
```

**Connection:**
- Frontend uses Next.js API route at `/api/copilotkit`
- API route uses `@ag-ui/client` HttpAgent
- HttpAgent connects to backend `/api/chat`

## CORS Configuration

**Backend:** `backend/config.py`
```python
CORS_ORIGINS = "http://localhost:3000,http://localhost:8080"
```

Both frontends are allowed by default. Additional origins can be added via environment variable:
```bash
export CORS_ORIGINS="http://localhost:3000,http://localhost:8080,http://custom-domain:3000"
```

## Testing Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### AG-UI Chat (requires valid RunAgentInput)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "threadId": "test-thread",
    "runId": "test-run",
    "messages": [{"id": "1", "role": "user", "content": "Hello"}],
    "state": {},
    "tools": [],
    "context": [],
    "forwardedProps": {}
  }'
```

## Event Flow Example

Complete flow for a simple question:

```
1. Frontend sends POST to /api/chat
2. Backend responds with SSE stream:
   → RUN_STARTED
   → TEXT_MESSAGE_START
   → TEXT_MESSAGE_CONTENT (streamed)
   → TEXT_MESSAGE_CONTENT (streamed)
   → ... (more content)
   → TEXT_MESSAGE_END
   → STATE_SNAPSHOT
   → RUN_FINISHED
3. Frontend closes SSE connection
```

## Error Handling

**Network Errors:**
- Frontend should handle connection failures
- Retry logic recommended for transient failures

**Backend Errors:**
- Returned as `RUN_ERROR` events
- PatternFly renders as inline Alert components
- CopilotKit displays error in chat

**LLM Errors:**
- OpenAI API failures trigger `RUN_ERROR`
- Error message includes details in `error.body`

## Implementation Details

**Backend Library:** `ag-ui-adk`
- Automatically creates `/api/chat` endpoint
- Handles SSE streaming
- Converts ADK agent responses to AG-UI events
- Manages session state

**Session Management:**
- In-memory session storage (default)
- 1-hour timeout (configurable)
- Thread/Run IDs track conversation state

## References

- [AG-UI Protocol Specification](https://github.com/ag-ui-protocol/ag-ui)
- [ag-ui-adk Library](https://github.com/ag-ui-protocol/ag-ui-adk)
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- Backend implementation: `backend/main.py`
- PatternFly integration: `source/observability-assistant-ui/src/hooks/useAgUiStream.ts`
- CopilotKit integration: `frontend/app/api/copilotkit/route.ts`

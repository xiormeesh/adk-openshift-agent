# Playwright Testing Guide

This document provides information about testing the frontend applications using Playwright MCP server.

## Available Frontends

### 1. PatternFly Frontend (Port 3000)

**Location:** `/source/observability-assistant-ui`
**URL:** http://localhost:3000/
**Framework:** Vite + React + PatternFly Chatbot
**Title:** "Observability Assistant"

#### Starting the Frontend
```bash
cd /source/observability-assistant-ui
make dev
```

#### UI Elements
- **Chat Interface:** PatternFly Chatbot component
- **Input Field:** `textbox "Ask about your cluster..."`
- **Messages:** Displayed in region "Scrollable message log"
- **Message Format:**
  - User messages: `region "Message from user - [timestamp]"`
  - Assistant messages: `region "Message from bot - [timestamp]"`
  - Supports markdown, tool calls, steps, and Prometheus charts

#### Demo vs Production Mode
- **Default:** Production mode (connects to backend)
- **Toggle:** Available in UI header via "Chatbot options" button
- **Storage:** Mode persisted in localStorage under `app-mode` key
- **Demo Mode:** Simulates responses locally without backend
- **Production Mode:** Connects to backend at http://localhost:8000 via proxy

#### Console Logs
When in production mode, browser console shows:
- `[AG-UI] OUT:` - Requests to backend
- `[AG-UI] IN:` - Events from backend (RUN_STARTED, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END, RUN_FINISHED)

#### Testing Example
```typescript
// Navigate
await browser_navigate({ url: "http://localhost:3000/" })

// Send message
await browser_type({
  element: "textbox \"Ask about your cluster...\"",
  ref: "e25", // Reference from snapshot
  text: "what is the latest OpenShift version?",
  submit: true
})

// Wait for response
await browser_wait_for({ textGone: "Loading message" })

// Take screenshot
await browser_take_screenshot({ filename: "test-result.png" })
```

---

### 2. Next.js + CopilotKit Frontend (Port 8080)

**Location:** `/frontend`
**URL:** http://localhost:8080/
**Framework:** Next.js + CopilotKit + React
**Title:** "OpenShift AI Assistant"

#### Starting the Frontend
```bash
cd /frontend
npm run dev
```

#### UI Elements
- **Chat Interface:** CopilotKit chat component
- **Input Field:** `textbox "Type a message..."`
- **Initial Message:** "Hi! I can answer questions about Kubernetes and OpenShift. How can I help you today?"
- **Action Buttons:** Regenerate, Copy, Thumbs up, Thumbs down
- **Footer:** "Powered by CopilotKit"

#### Backend Connection
- **Endpoint:** `/api/copilotkit` (Next.js API route)
- **Backend URL:** http://localhost:8000 (via environment variable `NEXT_PUBLIC_BACKEND_URL`)
- **Protocol:** AG-UI via HttpAgent
- **Agent Name:** `openshift_assistant`

#### Testing Example
```typescript
// Navigate
await browser_navigate({ url: "http://localhost:8080/" })

// Send message
await browser_type({
  element: "textbox \"Type a message...\"",
  ref: "e37", // Reference from snapshot
  text: "what are the networking options for Openshift",
  submit: false
})

// Click send button
await browser_click({
  element: "button \"Send\"",
  ref: "e23"
})

// Wait for response (button changes from "Stop" to "Send" when done)
// Check snapshot for completion

// Take screenshot
await browser_take_screenshot({ filename: "copilotkit-test.png" })
```

---

## Backend Connection

Both frontends connect to the same backend:
- **Backend URL:** http://localhost:8000
- **Protocol:** AG-UI
- **Framework:** FastAPI + ADK + LiteLLM
- **Model:** OpenAI GPT-4 Turbo

### Starting the Backend
```bash
cd backend/
poetry run dev
```

---

## Common Testing Patterns

### 1. Basic Question-Answer Test

```typescript
// Navigate to frontend
await browser_navigate({ url: "http://localhost:3000/" })

// Get fresh snapshot to get element references
await browser_snapshot()

// Type question
await browser_type({
  element: "textbox \"Ask about your cluster...\"",
  ref: "eXX", // Use ref from snapshot
  text: "your question here",
  submit: true
})

// Wait for completion
await browser_wait_for({ textGone: "Loading message" })

// Capture result
await browser_take_screenshot({ filename: "result.png" })
```

### 2. Clear localStorage (PatternFly)

```typescript
// Clear demo mode setting to use default (production)
await browser_evaluate({
  function: "() => { localStorage.removeItem('app-mode'); }"
})

// Refresh page
await browser_navigate({ url: "http://localhost:3000/" })
```

### 3. Check Console Logs

```typescript
// Get console messages
await browser_console_messages({ level: "info" })

// Look for AG-UI protocol events:
// [AG-UI] OUT: {...}
// [AG-UI] IN: {...}
```

---

## Testing Checklist

When testing either frontend:

- [ ] Frontend starts successfully
- [ ] Backend is running at http://localhost:8000
- [ ] Page loads without errors
- [ ] Input field is accessible
- [ ] Can send a test question
- [ ] Response streams from backend
- [ ] Response completes successfully
- [ ] Console shows AG-UI events (production mode)
- [ ] No network errors in console
- [ ] Messages render correctly (markdown, formatting)

---

## Troubleshooting

### PatternFly Frontend (Port 3000)

**Issue:** Shows demo responses instead of backend responses
**Solution:**
1. Check if in demo mode (toggle in UI header)
2. Clear localStorage: `localStorage.removeItem('app-mode')`
3. Refresh page
4. Verify backend is running

**Issue:** Proxy errors
**Solution:** Check `vite.config.ts` proxy configuration points to correct backend port

### Next.js Frontend (Port 8080)

**Issue:** 404 errors or "agent not found"
**Solution:**
1. Verify backend is running at http://localhost:8000
2. Check `/frontend/app/api/copilotkit/route.ts` has correct backend URL
3. Verify agent name matches: `openshift_assistant`

**Issue:** No response streaming
**Solution:**
1. Check browser console for errors
2. Verify `NEXT_PUBLIC_BACKEND_URL` environment variable
3. Test backend directly: `curl http://localhost:8000/health`

---

## Screenshots Location

Playwright screenshots are saved to:
```
.playwright-mcp/
```

---

## Updating This Document

**When to update:**
- Frontend ports change
- New frontend added
- UI elements change (different textbox labels, button names)
- Backend endpoint changes
- New features added (tool calls, charts, etc.)

**How to update:**
1. Test the changes manually with Playwright
2. Update relevant sections in this document
3. Update testing examples with new element references
4. Add new troubleshooting items if needed
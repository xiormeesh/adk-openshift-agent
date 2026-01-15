# ADK OpenShift Agent - Frontend

Next.js frontend with CopilotKit providing a chat interface for the AI assistant.

## Architecture

```
Frontend (CopilotChat) -> Next.js API Route (/api/copilotkit)
                       -> HttpAgent (@ag-ui/client)
                       -> AG-UI Protocol
                       -> Backend (FastAPI)
                       -> ADK Agent
                       -> OpenAI
```

## Quick Start

### Prerequisites

- Node.js 24+
- Backend running on http://localhost:8000

### Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file (optional):
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

Frontend runs on http://localhost:8080

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   └── copilotkit/
│   │       └── route.ts   # API route connecting to backend
│   ├── page.tsx           # Main chat interface (CopilotChat)
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── package.json           # Dependencies
└── .env.local            # Environment variables (not in git)
```

## Key Files

### app/page.tsx

Main chat interface using CopilotChat component.

**Key features:**
- Full-page chat interface (not popup)
- Header with app title
- Connects via `/api/copilotkit` route

**Code:**
```typescript
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

export default function Home() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="openshift_assistant"
    >
      <div className="flex flex-col h-screen">
        <header>...</header>
        <CopilotChat ... />
      </div>
    </CopilotKit>
  );
}
```

### app/api/copilotkit/route.ts

Next.js API route that connects CopilotKit to the ADK backend via AG-UI protocol.

**Code:**
```typescript
import { CopilotRuntime, ExperimentalEmptyAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";

const runtime = new CopilotRuntime({
  agents: {
    openshift_assistant: new HttpAgent({
      url: "http://localhost:8000/"
    }),
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter: new ExperimentalEmptyAdapter(),
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
};
```

## Configuration

### Environment Variables

**`.env.local`** (optional):
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

### Agent Name

The agent name `"openshift_assistant"` must match the backend agent name in `backend/agent/agent.py`.

## Current Status

✅ **Working:**
- Next.js API route proxy to backend
- CopilotChat full-page interface (not popup)
- Basic Q&A with OpenAI
- AG-UI protocol integration

## How It Works

### Architecture Flow

```
CopilotChat (page.tsx)
    ↓
CopilotKit (runtimeUrl="/api/copilotkit")
    ↓
Next.js API Route (route.ts)
    ↓
HttpAgent (AG-UI client)
    ↓
FastAPI Backend (AG-UI protocol)
    ↓
ADK Agent
```

### Key Components

1. **CopilotKit Provider** (page.tsx): Configures runtime connection
   - `runtimeUrl`: Points to Next.js API route `/api/copilotkit`
   - `agent`: Agent name (must match backend)

2. **CopilotChat** (page.tsx): Full-page chat interface
   - `instructions`: System prompt
   - `labels`: UI text customization

3. **API Route** (route.ts): Proxy between frontend and backend
   - `CopilotRuntime`: Manages agent connections
   - `HttpAgent`: Connects to backend via AG-UI protocol
   - `ExperimentalEmptyAdapter`: For single-agent setups

## Dependencies

Key packages:
- `@copilotkit/react-core` - Core CopilotKit functionality
- `@copilotkit/react-ui` - UI components (CopilotChat)
- `@copilotkit/runtime` - Runtime for API routes
- `@ag-ui/client` - AG-UI protocol client (HttpAgent)
- `next` - Next.js framework
- `react` - React library

## Development Commands

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Troubleshooting

### "Failed to connect to backend"

**Cause:** Backend not running or wrong URL.

**Fix:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_BACKEND_URL` in `.env.local`
3. Check CORS settings in backend allow `http://localhost:8080`

### "Agent not found"

**Cause:** Agent name mismatch.

**Fix:**
- Frontend: Check `agent="openshift_assistant"` in `page.tsx`
- Backend: Check agent name in `backend/agent/agent.py`
- Both must match exactly

### Chat interface not showing

**Cause:** Missing CopilotKit styles.

**Fix:**
- Verify `import "@copilotkit/react-ui/styles.css"` in `page.tsx`
- Check browser console for errors

## Additional Resources

- **CopilotKit Docs:** https://docs.copilotkit.ai/
- **Backend README:** `../backend/README.md`
- **Tech Stack:** `../TECH_STACK.md`

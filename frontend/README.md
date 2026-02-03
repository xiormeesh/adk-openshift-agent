# Frontend - CopilotKit Chat Interface

Next.js + CopilotKit frontend for the OpenShift AI Assistant.

## Quick Start

**Prerequisites:** Node.js 24+, Backend running on http://localhost:8000

```bash
npm install
npm run dev  # Runs on http://localhost:8080
```

## Architecture

```
CopilotChat UI → /api/copilotkit (Next.js route) → HttpAgent (AG-UI) → Backend (http://localhost:8000/api/chat)
```

## Key Files

- **`app/page.tsx`**: Main chat interface using `CopilotChat` component
- **`app/api/copilotkit/route.ts`**: API route connecting to backend via AG-UI protocol

## Configuration

**`.env.local`** (optional):
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

**Agent Name:** Must be `openshift_assistant` (matches backend `root_agent` name)

## How It Works

1. **page.tsx**: CopilotKit provider with `runtimeUrl="/api/copilotkit"` and `agent="openshift_assistant"`
2. **route.ts**: Creates `HttpAgent` pointing to `${BACKEND_URL}/api/chat`
3. **Backend**: AG-UI endpoint at `/api/chat` handles requests from HttpAgent

## Troubleshooting

**Connection failed:**
```bash
curl http://localhost:8000/health  # Verify backend is running
```

**Agent not found:** Ensure `agent="openshift_assistant"` in `page.tsx` matches backend agent name

**Chat not showing:** Check `import "@copilotkit/react-ui/styles.css"` in `page.tsx`

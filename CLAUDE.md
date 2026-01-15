# Project Instructions for Claude

## Project Goal

An agentic chatbot to answer questions about OpenShift and help troubleshoot an OpenShift cluster connecting to its observability data (metrics, alerts, logs, traces, events) as well as provide information and evaluation of the cluster's health status.

## Critical Development Principles

### 1. Minimal Code Philosophy

**This is a proof of concept that will be read frequently.**

- ✅ **ONLY implement features explicitly requested**
- ❌ **DO NOT add features "just in case"**
- ❌ **DO NOT future-proof the code**
- ❌ **DO NOT add abstractions for potential future use**
- ✅ **Keep the codebase as small and readable as possible**

### 2. Strict Change Protocol

When the user requests a change:

1. **Do EXACTLY what is requested - nothing more**
2. **Do not add:**
   - Extra error handling for edge cases not mentioned
   - Additional configuration options "for flexibility"
   - Helper functions for one-time operations
   - Comments explaining potential future uses
   - Type annotations to code that doesn't have them
   - Documentation to code you didn't change

3. **Ask before adding anything beyond the request**

### 3. Test Before Adding Complexity

**MANDATORY workflow for every phase:**

1. Implement the requested feature
2. Test that it works
3. Document what was added
4. Get user confirmation before moving to next feature

**Do not:**
- Implement multiple features at once
- Move to next phase without user verification
- Add "related improvements" while implementing a feature

### 4. Documentation Standards

- Document **what exists**, not what could exist
- Keep README files focused on **current functionality**
- Remove outdated documentation immediately
- Mark non-working features clearly (✅ Working / ❌ Not Working)

### 5. Frontend Development

**IMPORTANT: The user has NO frontend development experience.**

When making ANY frontend changes:

1. **Explain in detail before making changes:**
   - What you're changing and why
   - Why this approach is the best choice
   - What alternatives exist and why you're not using them
   - What the user should expect to see

2. **After making changes, explain:**
   - What files were changed
   - What each change does
   - How to verify it works

3. **Use simple language:**
   - Avoid frontend jargon without explanation
   - Explain React/Next.js concepts when needed
   - Don't assume knowledge of npm, components, hooks, etc.

4. **Think extra carefully:**
   - Is this change necessary for the requested feature?
   - Is this the simplest way to achieve it?
   - Could this confuse someone unfamiliar with frontend development?

**Example of good explanation:**
> "I'm removing the `components/` folder because it's empty and Next.js doesn't require it. Next.js only needs the `app/` folder for pages. We can recreate `components/` later if we need to share code between pages."

**Example of bad explanation:**
> "Removing unused components directory."

## Technical Documentation

**CRITICAL:** Before making changes to the stack integration, read `TECH_STACK.md`.

`TECH_STACK.md` contains comprehensive documentation about:
- How ADK (Agent Development Kit) works
- How AG-UI protocol connects frontends to ADK agents
- How CopilotKit integrates with ADK via AG-UI
- Complete integration patterns and troubleshooting

**Always consult TECH_STACK.md when:**
- Working on frontend ↔ backend integration
- Debugging "agent not found" errors
- Adding new agents or tools
- User asks "how does X work?"

## Project Structure

### Backend (Python)
- **Files:** `main.py`, `agent/agent.py`, `config.py`
- **Key endpoints:** `/` (health), `/health`, AG-UI protocol endpoints (auto-generated)
- **Stack:** FastAPI + ADK + AG-UI + LiteLLM + OpenAI
- **Port:** 8000

### Frontend (Next.js)
- **Files:** `app/page.tsx`, `app/api/copilotkit/route.ts`
- **Stack:** Next.js + CopilotKit + AG-UI client
- **Port:** 8080

## Current Phase Status

See `PLANNER.md` for phase definitions.

**Current Phase:** Phase 2 (CopilotKit frontend integration)

**Before moving to next phase:**
- User must verify current phase works
- All acceptance criteria must pass
- Documentation must be updated

## Development Workflow

### When User Requests a Feature

```
1. Read the request carefully
2. Confirm understanding (ask questions if unclear)
3. Implement ONLY what was requested
4. Test the implementation
5. Update documentation if relevant
6. Report completion with test results
7. Wait for user verification before continuing
```

### When User Reports a Bug

```
1. Reproduce the issue
2. Identify root cause
3. Fix ONLY the bug (no "while I'm here" fixes)
4. Test the fix
5. Report what was fixed
```

### What NOT to Do

❌ "I also noticed X could be improved, so I fixed that too"
❌ "I added error handling for edge case Y just in case"
❌ "I refactored Z to make it more maintainable"
❌ "I added comments explaining future extensibility"
❌ "I created a helper function for this 3-line operation"

✅ "I implemented exactly what you requested"
✅ "Would you like me to also handle X?"
✅ "I noticed Y - should I address that separately?"

## Technical Context

**See TECH_STACK.md for complete documentation.** Below is a quick reference.

### ADK + AG-UI Pattern (Current)

**Backend:**
```python
from ag_ui_adk import add_adk_fastapi_endpoint
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model=LiteLlm(model="openai/gpt-4-turbo-preview"),
    name="my_agent",
    instruction="..."
)

add_adk_fastapi_endpoint(app, root_agent, path="/")  # That's it!
```

**Frontend:**
```typescript
import { HttpAgent } from "@ag-ui/client";

const runtime = new CopilotRuntime({
  agents: {
    my_agent: new HttpAgent({ url: "http://localhost:8000/" })
  }
});
```

**Key points:**
- `add_adk_fastapi_endpoint()` auto-generates all necessary endpoints
- No manual session management needed
- Agent name must match in backend and frontend
- HttpAgent points to backend **root** URL

### MCP Integration (Phase 3+)
- Kubernetes MCP: localhost:8001 (when enabled)
- Observability MCP: localhost:8002 (future)
- Currently commented out in `agent/agent.py` - uncomment when Phase 3 starts

### Architecture
```
Frontend (localhost:8080)
  ↓
CopilotKit
  ↓
/api/copilotkit (Next.js route)
  ↓
HttpAgent (@ag-ui/client)
  ↓
AG-UI Protocol
  ↓
add_adk_fastapi_endpoint (backend:8000)
  ↓
root_agent (ADK)
  ↓
OpenAI
```

## Code Quality Standards

### Python
- Clear variable names
- Docstrings only where adding real value
- No "just in case" imports
- No unused functions
- Type hints where they clarify, not everywhere

### TypeScript/React
- Functional components
- Minimal abstractions
- Clear prop types
- No premature optimization

### General
- If you're about to add a comment explaining complexity, simplify the code instead
- If you're creating a helper for one use, inline it
- If you're adding configuration for "flexibility", remove it

## Testing Expectations

### After Each Change
```bash
# Backend health check
curl http://localhost:8000/health

# AG-UI info endpoint (auto-generated)
curl http://localhost:8000/info

# Full integration test
# 1. Start backend: cd backend && poetry run dev
# 2. Start frontend: cd frontend && npm run dev
# 3. Open http://localhost:8080
# 4. Test chat in popup
```

### Phase Completion
- All acceptance criteria in PLANNER.md must pass
- User must manually verify functionality
- Documentation must reflect current state

## Common Patterns

### Reading Files
- Read file before editing (required by tools)
- Only edit what needs changing
- Don't reformat code you didn't touch

### Adding Dependencies
```bash
# Backend
poetry add package-name

# Frontend
cd frontend && npm install package-name
```

### Debugging
1. Check backend logs: `tail -f /tmp/claude/.../<task-id>.output`
2. Check frontend console (user reports errors)
3. Fix root cause, not symptoms

## Remember

This is a **proof of concept**, not a production system:
- Readability > Robustness
- Simplicity > Scalability
- Working > Perfect
- Tested > Theoretical

**Every line of code added increases maintenance burden.**
**Every feature added increases complexity.**
**Only add what's explicitly needed.**

## Questions to Ask Yourself

Before adding code:
- ✓ Did the user explicitly request this?
- ✓ Is this the simplest way to implement it?
- ✓ Am I solving an actual problem or a potential problem?
- ✓ Would removing this code break what was requested?

If answer to last question is "no", don't add the code.

## Communication Style

- Be concise
- Report what was done, not what could be done
- Ask before adding extras
- Confirm understanding before implementing
- Test and show results

## File Change Protocol

**Before making changes:**
1. Read current file state
2. Understand what needs to change
3. Change ONLY what's necessary
4. Don't add/remove features not mentioned

**Dead code removal:**
- Only remove if explicitly requested
- Or if it's clearly unused imports from a change you just made

## Summary

**Golden Rule:** If the user didn't ask for it, don't add it.

The user values:
1. Minimal, readable code
2. Following instructions exactly
3. Testing before complexity
4. Clear documentation of current state
5. Phased, verified development

Honor these values in every interaction.

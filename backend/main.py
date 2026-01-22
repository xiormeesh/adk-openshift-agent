"""
FastAPI server for ADK OpenShift Agent.

This backend exposes the ADK agent via AG-UI protocol for frontend integration.
Supports multiple frontends: CopilotKit (Next.js) and PatternFly (observability-assistant-ui).

Architecture:
    Frontend -> AG-UI Protocol (POST /api/chat, SSE streaming) -> ADK Agent -> OpenAI

Supported Frontends:
    - CopilotKit (localhost:8080): Next.js with HttpAgent
    - PatternFly (localhost:3000): React + Vite with direct SSE streaming

Key Components:
    - ADK (Agent Development Kit): Google's framework for building AI agents
    - AG-UI: Protocol for connecting frontends to ADK agents via SSE
    - LiteLLM: Adapter for using OpenAI models with ADK
    - add_adk_fastapi_endpoint(): Exposes the agent via AG-UI protocol at /api/chat
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

from agent import root_agent
from config import config

# Configure logging - DEBUG level shows ADK internal flow
# Including: system instructions, conversation history, tool definitions, tool invocations
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("adk_debug.log"),
        logging.StreamHandler()
    ]
)

# Set specific logger levels for ADK components
logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("litellm").setLevel(logging.DEBUG)
logging.getLogger("ag_ui_adk").setLevel(logging.INFO)  # Reduce noise from AG-UI events
logging.getLogger("watchfiles").setLevel(logging.WARNING)  # Reduce noise from file watcher
logging.getLogger("uvicorn").setLevel(logging.INFO)  # Reduce uvicorn noise

logger = logging.getLogger(__name__)

# Validate configuration
config.validate()

# Create FastAPI app
app = FastAPI(
    title="ADK OpenShift Agent API",
    description="AI-powered Kubernetes/OpenShift cluster management",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wrap the ADK agent with AG-UI middleware
adk_agent = ADKAgent(
    adk_agent=root_agent,
    app_name=config.AGENT_NAME,
    user_id="default_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Expose ADK agent via AG-UI protocol at /api/chat
add_adk_fastapi_endpoint(app, adk_agent, path="/api/chat")


@app.get("/")
async def root():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "agent": config.AGENT_NAME,
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check with configuration info."""
    return {
        "status": "healthy",
        "agent": config.AGENT_NAME,
        "model": config.OPENAI_MODEL,
        "ag_ui": "enabled"
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info(f"Starting {config.AGENT_NAME}")
    logger.info(f"Model: {config.OPENAI_MODEL}")
    logger.info(f"CORS origins: {config.CORS_ORIGINS}")


def dev():
    """
    Run development server with auto-reload and debug logging.

    Usage:
        poetry run dev

    This is configured in pyproject.toml:
        [tool.poetry.scripts]
        dev = "main:dev"
    """
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="debug"
    )


if __name__ == "__main__":
    dev()

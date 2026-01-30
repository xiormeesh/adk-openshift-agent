"""
Configuration management for the ADK OpenShift Agent backend.

This module loads configuration from environment variables (.env file).

Required Environment Variables:
    OPENAI_API_KEY: Your OpenAI API key (required)
    GOOGLE_API_KEY: Your Google API key for Gemini and search (required)

Optional Environment Variables:
    OPENAI_MODEL: OpenAI model to use (default: gpt-5-nano)
    GEMINI_MODEL: Gemini model to use (default: gemini-2.5-flash)
    BACKEND_HOST: Server host (default: localhost)
    BACKEND_PORT: Server port (default: 8000)
    CORS_ORIGINS: Comma-separated list of allowed origins (default: http://localhost:3000,http://localhost:8080)
    KUBECONFIG: Path to kubeconfig file (default: ~/.kube/config)

Example .env file:
    OPENAI_API_KEY=sk-...
    GOOGLE_API_KEY=...
    OPENAI_MODEL=gpt-5-nano
    GEMINI_MODEL=gemini-2.5-flash
    BACKEND_HOST=localhost
    BACKEND_PORT=8000
    CORS_ORIGINS=http://localhost:3000,http://localhost:8080
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")

    # Google/Gemini Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Server Configuration
    HOST = os.getenv("BACKEND_HOST", "localhost")
    PORT = int(os.getenv("BACKEND_PORT", "8000"))

    # CORS Configuration (for local development)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")

    # MCP Server Configuration
    KUBECONFIG = os.getenv("KUBECONFIG", str(Path.home() / ".kube" / "config"))

    # Agent Configuration
    AGENT_NAME = "openshift_assistant"
    AGENT_DESCRIPTION = (
        "An AI assistant that helps you manage Kubernetes and OpenShift clusters. "
        "I can view resources, check logs, and help troubleshoot issues using natural language."
    )

    @classmethod
    def validate(cls):
        """
        Validate required configuration.

        Raises:
            ValueError: If OPENAI_API_KEY or GOOGLE_API_KEY is not set

        Returns:
            bool: True if validation passes
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        return True


# Singleton instance
config = Config()

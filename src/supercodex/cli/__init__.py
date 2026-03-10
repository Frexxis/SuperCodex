"""
SuperCodex CLI

Commands:
    - supercodex install                   # Install/update Codex skills
    - supercodex mcp                       # Manage Codex MCP config
    - supercodex doctor                    # Check installation health
    - supercodex version                   # Show version
"""

from .main import main

__all__ = ["main"]

"""
SuperCodex Framework

AI-enhanced development framework for Codex CLI.
Provides a pytest plugin for PM-agent-style workflows and an optional skills system.
"""

from .__version__ import __version__

__author__ = "NomenAK, Mithun Gowda B"

# Expose main components
from .pm_agent.confidence import ConfidenceChecker
from .pm_agent.reflexion import ReflexionPattern
from .pm_agent.self_check import SelfCheckProtocol

__all__ = [
    "ConfidenceChecker",
    "SelfCheckProtocol",
    "ReflexionPattern",
    "__version__",
]

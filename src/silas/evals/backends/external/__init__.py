"""External-framework subprocess backends (Hermes Agent, OpenClaw)."""

from silas.evals.backends.external.hermes_agent import HermesBackend
from silas.evals.backends.external.openclaw import OpenClawBackend

__all__ = ["HermesBackend", "OpenClawBackend"]

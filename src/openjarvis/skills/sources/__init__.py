"""Skill source resolvers — Hermes, OpenClaw, generic GitHub."""

from silas.skills.sources.base import ResolvedSkill, SourceResolver
from silas.skills.sources.github import GitHubResolver
from silas.skills.sources.hermes import HERMES_REPO_URL, HermesResolver
from silas.skills.sources.openclaw import OPENCLAW_REPO_URL, OpenClawResolver

__all__ = [
    "GitHubResolver",
    "HERMES_REPO_URL",
    "HermesResolver",
    "OPENCLAW_REPO_URL",
    "OpenClawResolver",
    "ResolvedSkill",
    "SourceResolver",
]

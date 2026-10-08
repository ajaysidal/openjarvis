"""Skill system — reusable multi-tool compositions."""

from silas.skills.dependency import (
    DependencyCycleError,
    DepthExceededError,
    build_dependency_graph,
    compute_capability_union,
    validate_dependencies,
)
from silas.skills.executor import SkillExecutor, SkillResult
from silas.skills.importer import ImportResult, SkillImporter
from silas.skills.loader import (
    discover_skills,
    load_skill,
    load_skill_directory,
    load_skill_markdown,
)
from silas.skills.manager import SkillManager
from silas.skills.parser import SkillParseError, SkillParser
from silas.skills.tool_adapter import SkillTool
from silas.skills.tool_translator import TOOL_TRANSLATION, ToolTranslator
from silas.skills.types import SkillManifest, SkillStep

__all__ = [
    "DependencyCycleError",
    "DepthExceededError",
    "ImportResult",
    "SkillExecutor",
    "SkillImporter",
    "SkillManager",
    "SkillManifest",
    "SkillParseError",
    "SkillParser",
    "SkillResult",
    "SkillStep",
    "SkillTool",
    "TOOL_TRANSLATION",
    "ToolTranslator",
    "build_dependency_graph",
    "compute_capability_union",
    "discover_skills",
    "load_skill",
    "load_skill_directory",
    "load_skill_markdown",
    "validate_dependencies",
]

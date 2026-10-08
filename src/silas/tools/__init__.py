"""Tools primitive — tool system with ABC interface and built-in tools."""

from __future__ import annotations

from silas.tools._stubs import BaseTool, ToolExecutor, ToolSpec

# Import built-in tools to trigger @ToolRegistry.register() decorators.
# Each is wrapped in try/except so the package loads even before the
# individual tool modules are created.
try:
    import silas.tools.calculator  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.think  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.retrieval  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.llm_tool  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.file_read  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.web_search  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.weather  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.code_interpreter  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.code_interpreter_docker  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.repl  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.storage_tools  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.mcp_adapter  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.channel_tools  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.http_request  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.docker_shell_exec  # noqa: F401
    import silas.tools.shell_exec  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.memory_manage  # noqa: F401
except ImportError:
    pass
try:
    import silas.tools.user_profile_manage  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.skill_manage  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.file_write  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.apply_patch  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.git_tool  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.db_query  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.pdf_tool  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.image_tool  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.audio_tool  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.knowledge_tools  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.text_to_speech  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.digest_collect  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.scan_chunks  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.knowledge_sql  # noqa: F401
except ImportError:
    pass

try:
    import silas.tools.apple_calendar  # noqa: F401
except ImportError:
    pass

__all__ = ["BaseTool", "ToolExecutor", "ToolSpec"]

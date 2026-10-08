"""Bundle dataclasses that group cohesive subsystems of JarvisSystem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from silas.agents._stubs import BaseAgent
    from silas.agents.executor import AgentExecutor
    from silas.agents.manager import AgentManager
    from silas.agents.scheduler import AgentScheduler
    from silas.scheduler.scheduler import TaskScheduler
    from silas.scheduler.store import SchedulerStore
    from silas.security.audit import AuditLogger
    from silas.security.boundary import BoundaryGuard
    from silas.security.capabilities import CapabilityPolicy
    from silas.telemetry.gpu_monitor import GpuMonitor
    from silas.telemetry.store import TelemetryStore
    from silas.traces.collector import TraceCollector
    from silas.traces.store import TraceStore


@dataclass
class SecurityContext:
    """Security policy, audit, and boundary enforcement."""

    capability_policy: Optional[CapabilityPolicy] = None
    audit_logger: Optional[AuditLogger] = None
    boundary_guard: Optional[BoundaryGuard] = None
    rate_limiter: Optional[Any] = None


@dataclass
class Observability:
    """Telemetry, traces, and hardware monitoring."""

    telemetry_store: Optional[TelemetryStore] = None
    trace_store: Optional[TraceStore] = None
    trace_collector: Optional[TraceCollector] = None
    gpu_monitor: Optional[GpuMonitor] = None


@dataclass
class AgentRuntime:
    """Active agent and agent lifecycle managers."""

    agent: Optional[BaseAgent] = None
    agent_name: str = ""
    manager: Optional[AgentManager] = None
    scheduler: Optional[AgentScheduler] = None
    executor: Optional[AgentExecutor] = None


@dataclass
class Scheduling:
    """Task scheduler and its persistent store."""

    store: Optional[SchedulerStore] = None
    runner: Optional[TaskScheduler] = None

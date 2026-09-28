"""Learning primitive -- router policies, reward functions, learning."""

from __future__ import annotations

from silas.learning._stubs import (
    QueryAnalyzer,
    RewardFunction,
    RouterPolicy,
    RoutingContext,
)
from silas.learning.agents.agent_evolver import AgentConfigEvolver
from silas.learning.learning_orchestrator import LearningOrchestrator
from silas.learning.optimize.llm_optimizer import LLMOptimizer
from silas.learning.optimize.optimizer import OptimizationEngine
from silas.learning.optimize.store import OptimizationStore
from silas.learning.routing.complexity import (
    ComplexityQueryAnalyzer,
    score_complexity,
)
from silas.learning.routing.heuristic_reward import HeuristicRewardFunction
from silas.learning.routing.router import (
    HeuristicRouter,
    build_routing_context,
)
from silas.learning.training.data import TrainingDataMiner
from silas.learning.training.lora import HAS_TORCH, LoRATrainer, LoRATrainingConfig


def ensure_registered() -> None:
    """Ensure all learning policies are registered in RouterPolicyRegistry."""
    from silas.learning.routing.heuristic_policy import (
        ensure_registered as _reg_heuristic,
    )

    _reg_heuristic()

    from silas.learning.routing.learned_router import (
        ensure_registered as _reg_learned,
    )

    _reg_learned()

    # Intelligence training (optional deps)
    try:
        import silas.learning.intelligence  # noqa: F401
    except ImportError:
        pass

    # Orchestrator-specific training (optional deps)
    try:
        import silas.learning.intelligence.orchestrator  # noqa: F401
    except ImportError:
        pass

    # Agent optimizers (optional deps)
    try:
        import silas.learning.agents.dspy_optimizer  # noqa: F401
    except ImportError:
        pass
    try:
        import silas.learning.agents.gepa_optimizer  # noqa: F401
    except ImportError:
        pass
    try:
        import silas.learning.agents.ace_optimizer  # noqa: F401
    except ImportError:
        pass


__all__ = [
    "AgentConfigEvolver",
    "ComplexityQueryAnalyzer",
    "HAS_TORCH",
    "HeuristicRewardFunction",
    "HeuristicRouter",
    "LLMOptimizer",
    "LearningOrchestrator",
    "LoRATrainer",
    "LoRATrainingConfig",
    "OptimizationEngine",
    "OptimizationStore",
    "QueryAnalyzer",
    "RewardFunction",
    "RouterPolicy",
    "RoutingContext",
    "TrainingDataMiner",
    "build_routing_context",
    "ensure_registered",
    "score_complexity",
]

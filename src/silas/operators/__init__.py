"""Operators — persistent, scheduled autonomous agents."""

from silas.operators.loader import load_operator
from silas.operators.manager import OperatorManager
from silas.operators.types import OperatorManifest

__all__ = ["OperatorManifest", "OperatorManager", "load_operator"]

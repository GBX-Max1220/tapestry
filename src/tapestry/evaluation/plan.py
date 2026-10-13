"""Evaluation-plan coverage helpers for requirements readiness.

The project already has gate logic that can decide whether a result bundle
passes. This module adds the planning layer above it: a compact way to check
whether a proposed evaluation bundle covers the current minimum requirements.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from tapestry.evaluation.gates import BenchmarkKind, BenchmarkSpec, EvaluationGate

DEFAULT_REQUIRED_KINDS: list[BenchmarkKind] = [
    BenchmarkKind.CAPABILITY,
    BenchmarkKind.CULTURAL_ALIGNMENT,
    BenchmarkKind.SAFETY,
]


@dataclass(frozen=True)
class EvaluationPlanFinding:
    """One issue found while checking an evaluation plan."""

    kind: BenchmarkKind
    message: str


@dataclass(frozen=True)
class EvaluationPlanDecision:
    """Coverage decision for a proposed set of benchmark specs."""

    ready: bool
    findings: list[EvaluationPlanFinding] = field(default_factory=list)


@dataclass(frozen=True)
class EvaluationPlan:
    """
    A versioned, runner-neutral plan for benchmark coverage.

    Implementation Note: required_kinds is declared with
    `field(default_factory=lambda: DEFAULT_REQUIRED_KINDS)`
    to initialize with the default list. If you try
    `field(default=DEFAULT_REQUIRED_KINDS)`, you get errors
    when pytest tries to load this class!
    """

    specs: list[BenchmarkSpec] = field(default_factory=list)
    required_kinds: list[BenchmarkKind] = field(default_factory=lambda: DEFAULT_REQUIRED_KINDS)

    def __post_init__(self) -> None:
        if not self.specs:
            raise ValueError("EvaluationPlan requires at least one benchmark spec")

    @property
    def covered_required_kinds(self) -> frozenset[BenchmarkKind]:
        """Required benchmark kinds covered by at least one required spec."""
        return frozenset(spec.kind for spec in self.specs if spec.required and spec.kind in self.required_kinds)

    @property
    def missing_required_kinds(self) -> list[BenchmarkKind]:
        """Required benchmark kinds not represented by the plan."""
        covered = self.covered_required_kinds
        return [kind for kind in self.required_kinds if kind not in covered]

    def check_coverage(self) -> EvaluationPlanDecision:
        """Return whether the plan covers the configured required axes."""
        findings = [
            EvaluationPlanFinding(
                kind=kind,
                message=f"required evaluation kind {kind.value} is missing",
            )
            for kind in self.missing_required_kinds
        ]
        return EvaluationPlanDecision(ready=not findings, findings=findings)

    def gate(self) -> EvaluationGate:
        """Build a release gate from the plan specs."""
        return EvaluationGate(self.specs)


def required_kind_summary(specs: Iterable[BenchmarkSpec]) -> dict[str, int]:
    """Count required benchmark specs by kind for PR and runbook summaries."""
    counts: dict[str, int] = {}
    for spec in specs:
        if not spec.required:
            continue
        kind = BenchmarkKind(spec.kind)
        counts[kind.value] = counts.get(kind.value, 0) + 1
    return counts

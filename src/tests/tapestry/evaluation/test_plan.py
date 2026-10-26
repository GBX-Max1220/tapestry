"""Tests for evaluation-plan coverage helpers."""

from __future__ import annotations

from tapestry.evaluation import (
    BenchmarkConfig,
    BenchmarkKind,
    BenchmarkSpec,
    EvaluationPlan,
    required_kind_summary,
)


def _spec(benchmark_id: str, kind: BenchmarkKind, required: bool = True) -> BenchmarkSpec:
    return BenchmarkSpec(
        benchmark_id=benchmark_id,
        name=benchmark_id.replace("-", " ").title(),
        kind=kind,
        metric="score",
        config=BenchmarkConfig(
            task_version=f"{benchmark_id}/v1",
            dataset_revision="2026-08-01",
            prompt_template="zero-shot",
        ),
        threshold=0.7,
        required=required,
    )


def _in(value: str, seq: list[str]):
    try:
        assert seq.index(value) >= 0
    except ValueError as ve:
        assert False, str(ve)


def test_plan_is_ready_when_required_axes_are_present():
    """A plan is ready when capability, alignment, and safety are covered."""
    plan = EvaluationPlan(
        [
            _spec("capability-core", BenchmarkKind.CAPABILITY),
            _spec("cultural-alignment-smoke", BenchmarkKind.CULTURAL_ALIGNMENT),
            _spec("refusal-safety", BenchmarkKind.SAFETY),
            _spec("domain-extra", BenchmarkKind.DOMAIN, required=False),
        ]
    )

    decision = plan.check_coverage()

    assert decision.ready
    assert len(decision.findings) == 0
    _in("capability-core", list(plan.gate().specs.keys()))


def test_plan_reports_missing_required_axes():
    """Missing required benchmark axes are reported as findings."""
    plan = EvaluationPlan([_spec("capability-core", BenchmarkKind.CAPABILITY)])

    decision = plan.check_coverage()

    assert not decision.ready
    assert [finding.kind for finding in decision.findings] == [BenchmarkKind.CULTURAL_ALIGNMENT, BenchmarkKind.SAFETY]


def test_required_kind_summary_ignores_optional_specs():
    """Optional benchmarks are omitted from required-kind summaries."""
    summary = required_kind_summary(
        [
            _spec("capability-core", BenchmarkKind.CAPABILITY),
            _spec("domain-extra", BenchmarkKind.DOMAIN, required=False),
        ]
    )

    assert summary == {"capability": 1}

"""Tests for data-management capability checks."""

from __future__ import annotations

from tapestry.data import (
    REQUIRED_DATA_CAPABILITIES,
    DataParticipationMode,
    DataToolAssessment,
    allowed_modes_for_shared_training,
)


def test_complete_data_tool_assessment_has_no_findings():
    """A tool supporting all required capabilities has no findings."""
    assessment = DataToolAssessment(
        tool_name="candidate-catalog",
        supported_capabilities=REQUIRED_DATA_CAPABILITIES,
        viable_long_term=True,
        notes=[],
    )

    assert not assessment.missing_capabilities
    assert not assessment.findings()


def test_participant_private_mode_is_not_allowed_for_shared_training():
    """Private-only data is excluded from shared-training participation."""
    modes = allowed_modes_for_shared_training()

    assert DataParticipationMode.LOCAL_ONLY in modes
    assert DataParticipationMode.PARTICIPANT_PRIVATE not in modes

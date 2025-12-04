import pytest
from types import SimpleNamespace

from src.robocop_mcp.config import Rule, get_config
from src.robocop_mcp.mcp_check import Violation, get_violation_fix


@pytest.mark.asyncio
async def test_get_violation_fix_returns_default_message_for_unknown_rule(tmp_path, test_1):
    robot_file = tmp_path / "sample.robot"
    robot_file.write_text(test_1)

    mock_violation = Violation(
        file=robot_file,
        start_line=2,
        end_line=2,
        start_column=1,
        end_column=10,
        severity="W",
        rule_id="NotHere001",
        description="Missing documentation in 'Test Case' test case",
    )
    config = get_config()
    result = get_violation_fix(mock_violation, config)
    assert result == "No solution proposed fix found"


@pytest.mark.asyncio
async def test_get_violation_fix_returns_user_defined_instruction(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC01",
        description="Missing documentation",
    )
    config = SimpleNamespace(
        user_rules={
            "DOC01": Rule(
                rule_id="DOC01", instruction="Add documentation to the test case.", name="missing-doc-keyword"
            )
        },
        predefined_fixes={},
    )

    result = get_violation_fix(violation, config)
    assert result == "Add documentation to the test case."


@pytest.mark.asyncio
async def test_get_violation_fix_loads_instruction_from_file(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    instruction_file = tmp_path / "instruction.md"
    instruction_file.write_text("Detailed fix instructions.")
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC02",
        description="Another issue",
    )
    config = SimpleNamespace(
        user_rules={
            "DOC02": Rule(rule_id="DOC02", instruction=str(instruction_file), name="missing-doc-keyword")
        },
        predefined_fixes={},
        robocop_rules={},
    )

    result = get_violation_fix(violation, config)
    assert result == "Detailed fix instructions."


@pytest.mark.asyncio
async def test_get_violation_fix_fallback_for_unmapped_rules(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC03",
        description="Unmatched issue",
    )
    config = SimpleNamespace(
        user_rules={
            "DOC01": Rule(rule_id="DOC01", instruction="Some instruction", name="missing-doc-keyword")
        },
        predefined_fixes={},
        robocop_rules={},
    )

    result = get_violation_fix(violation, config)
    assert result == "No solution proposed fix found"


@pytest.mark.asyncio
async def test_get_violation_fix_uses_predefined_fix_when_available(tmp_path, test_3_duplicate_names):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_3_duplicate_names)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DUP01",
        description="There are duplicate test cases",
    )
    fix_proposal = "With a duplicate test names add a running index index in the test name with three digits."
    config = SimpleNamespace(
        user_rules={
            "DOC01": Rule(rule_id="DOC01", instruction="Some instruction", name="missing-doc-keyword")
        },
        predefined_fixes={
            "DUP01": Rule(
                rule_id="DUP01",
                instruction=fix_proposal,
                name="duplicated-test-cases",
            )
        },
        robocop_rules={},
    )
    result = get_violation_fix(violation, config)
    assert fix_proposal == result


@pytest.mark.asyncio
async def test_get_violation_fix_prioritizes_user_rules_over_predefined(tmp_path, test_3_duplicate_names):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_3_duplicate_names)
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DUP01",
        description="There are duplicate test cases",
    )
    fix_proposal = "With a duplicate test names add a running index index in the test name with three digits."
    config = SimpleNamespace(
        user_rules={
            "DUP01": Rule(rule_id="DUP01", instruction="Some instruction", name="duplicated-test-case")
        },
        predefined_fixes={
            "DUP01": Rule(
                rule_id="DUP01",
                instruction=fix_proposal,
                name="duplicated-test-cases",
            )
        },
        robocop_rules={},
    )
    result = get_violation_fix(violation, config)
    assert result == "Some instruction"


@pytest.mark.asyncio
async def test_get_violation_fix_loads_predefined_fix_from_file(tmp_path, test_1):
    sample_file = tmp_path / "sample.robot"
    sample_file.write_text(test_1)
    instruction_file = tmp_path / "predefined_fix.md"
    instruction_file.write_text("Predefined file instruction.")
    violation = Violation(
        file=sample_file,
        start_line=1,
        end_line=1,
        start_column=1,
        end_column=1,
        severity="W",
        rule_id="DOC02",
        description="Needs predefined fix",
    )
    config = SimpleNamespace(
        user_rules={},
        predefined_fixes={
            "DOC02": Rule(
                rule_id="DOC02",
                instruction=str(instruction_file),
                name="missing-doc-keyword",
            )
        },
        robocop_rules={},
    )

    result = get_violation_fix(violation, config)
    assert result == "Predefined file instruction."

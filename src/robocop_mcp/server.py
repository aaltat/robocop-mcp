# Copyright (c) 2025 Tatu Aalto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .config import get_config, logger, resolve_path
from .mcp_check import filter_violations, format_report, get_violation_fix, run_robocop
from .mcp_format import robocop_format

mcp = FastMCP("op-robocop-mcp")


@mcp.tool()
async def get_robocop_report(path: str | None) -> str:
    """
    Run RoboCop on the provided source code and return the report.

    Args:
        path (str | None): The path to folder or a file to analyze. If None, uses the
        current directory for analysis.

    Returns:
        str: The Robocop report in markdown format. Report by default contains 20 first violations
        of the same type. If there are other types of violations or there are more than 20 same type
        of violations, a note is added about how many more violations were found but not shown.
        Report contains at the end also a proposed fix for the first violation.

    Example if there is one Violation in path, which looks like this:
    Violation(
        file=WindowsPath('sample.robot'),
        line_number=2,
        end_line=2,
        column=1,
        end_column=15,
        severity='W',
        rule_id='DOC02',
        description="Missing documentation in 'this is a test' test case"
    )
    Then return value would look like this:
    # Robocop Report

    ## Violation for file sample.robot in line 2 rule DOC02

    description: Missing documentation in 'this is a test' test case
    start line: 2
    end line: 2
    start column: 1
    end column: 15
    file: C:\\path\\to\\sample.robot
    rule id: DOC02
    severity: WARNING

    All violations reported.

    ## Proposed fixe for violations
    The following fix is proposed: Add documentation to the 'this is a test' test case

    """
    path_resolved = resolve_path(path)
    logger.info("Running Robocop check on path: '%s'", path_resolved)
    report = await run_robocop(path_resolved)
    filter_report = filter_violations(report)
    if not filter_report:
        logger.info("No violations found.")
        return "# Robocop Report\n\nNo violations found."
    logger.info("Dump to markdown...")
    markdown_lines = ["# Robocop Report", ""]
    for item in filter_report:
        markdown_lines.extend(format_report(item))

    first_violation = filter_report[0]
    config = get_config()
    proposed_fix = get_violation_fix(first_violation, config)
    markdown_lines.extend(
        [
            "",
            "## Proposed fixe for violations",
            "",
            f"The following fix is proposed: {proposed_fix}",
        ],
    )
    if len(filter_report) < len(report):
        markdown_lines.append(f"\nand {len(report) - len(filter_report)} more violations not shown.")
    else:
        markdown_lines.append("\nAll violations reported.")
    return "\n".join(markdown_lines)


@mcp.tool()
async def run_robocop_format(path: str | None) -> str:
    """Runs RoboCop formatter on the given path or folder.

    Args:
        path (str | None): The path to folder or a file to format. If None, uses the
        current directory for analysis.
    Returns:
        str: A summary of the operation.
    """
    path_resolved = resolve_path(path)
    logger.info("Running Robocop format on path: '%s'", path_resolved)
    return await robocop_format(Path(path_resolved))


def main() -> None:
    "Main to run the robocop-mcp server."
    logger.info("Starting OP Robocop MCP...")
    config = get_config()
    if config.robocopmcp_config_file:
        logger.info("With %s file.", config.robocopmcp_config_file)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

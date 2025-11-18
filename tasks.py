from pathlib import Path

from invoke import Context, task

ROOT = Path(__file__).parent


@task
def utest(ctx: Context):
    ctx.run("coverage run -m pytest --approvaltests-use-reporter='PythonNativeReporter' ./utest")
    ctx.run("coverage html --omit='utest/*'")


@task
def lint(ctx: Context, fix: bool = False):
    """
    Run ruff and MyPy linters.

    Args:
        fix: Whether to auto-fix issues found by ruff check.

    """
    print("Run ruff format")
    ctx.run("ruff format .")
    ruff_check = ["ruff", "check"]
    if fix:
        ruff_check.append("--fix")
    ruff_check.append(".")
    print("run ruff check.")
    ctx.run(" ".join(ruff_check))
    print("Run MyPy")
    ctx.run("mypy src/robocop_mcp")

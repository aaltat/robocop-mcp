import shutil
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


@task
def clean(_: Context):
    """Clean up build artifacts and cache files"""
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree(".mypy_cache", ignore_errors=True)
    shutil.rmtree(".pytest_cache", ignore_errors=True)
    shutil.rmtree(".ruff_cache", ignore_errors=True)
    shutil.rmtree("htmlcov", ignore_errors=True)
    for folder in ROOT.glob("**/.DS_Store"):
        shutil.rmtree(folder, ignore_errors=True)


@task
def version(_: Context, version: str):
    """Set the version of the library __init__.py."""
    init_file = ROOT / "src" / "robocop_mcp" / "__init__.py"
    with init_file.open("r") as file:
        lines = file.readlines()
    for index, line in enumerate(lines):
        if line.startswith("__version__"):
            lines[index] = f'__version__ = "{version}"\n'
            break
    with init_file.open("w") as file:
        file.writelines(lines)
    print(f"Library version set to {version} in {init_file}.")

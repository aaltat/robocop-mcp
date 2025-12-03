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
import sys
from io import StringIO
from pathlib import Path

import typer
from robocop.run import format_files  # type: ignore

from .config import get_config, logger, set_robocop_config_file


class Capturing(list):
    def __enter__(self) -> "Capturing":
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringio_out = StringIO()
        sys.stderr = self._stringio_err = StringIO()
        return self

    def __exit__(self, *_: object) -> None:
        stdout_content = self._stringio_out.getvalue()
        stderr_content = self._stringio_err.getvalue()
        self.extend(stdout_content.splitlines())
        self.extend(stderr_content.splitlines())
        del self._stringio_out
        del self._stringio_err
        sys.stdout = self._stdout
        sys.stderr = self._stderr


async def robocop_format(path: Path) -> str:
    sources = [path]
    config = get_config()
    kwargs = {"sources": sources, "reruns": config.robocop_reruns}
    kwargs = set_robocop_config_file(config, kwargs)
    raised_error = None
    with Capturing() as output:
        try:
            format_files(**kwargs)
        except typer.Exit:
            pass
        except Exception as error:  # noqa
            logger.error("Error during RoboCop format: %s", error)
            raised_error = error
    report = "\n".join(output) if not raised_error else f"Error during formatting: {raised_error}"
    logger.info("RoboCop format completed with report: %s", report)
    return report

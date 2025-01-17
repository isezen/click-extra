# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""Utilities to execute external commands."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from textwrap import indent
from typing import Iterable, Mapping, Optional, Union, cast

from boltons.iterutils import flatten

from .colorize import default_theme

PROMPT = "► "
INDENT = " " * len(PROMPT)
"""Some CLI printing constants."""


EnvVars = Mapping[str, Optional[str]]


Arg = Union[str, Path, None]
Args = Iterable[Arg]
NestedArgs = Iterable[Union[Arg, Iterable["NestedArgs"]]]


def args_cleanup(*args: Arg | NestedArgs) -> tuple[str, ...]:
    """Flatten recursive iterables, remove all ``None``, and cast each element to
    strings.

    Helps serialize :py:class:`pathlib.Path` and other objects.

    It also allows for nested iterables and ``None`` values as CLI arguments for
    convenience. We just need to flatten and filters them out.
    """
    return tuple(str(arg) for arg in flatten(args) if arg is not None)


def format_cli(cmd, extra_env: EnvVars | None = None) -> str:
    """Simulate CLI rendering in terminal."""
    assert cmd
    cmd_str = default_theme.invoked_command(" ".join(cmd))

    extra_env_string = ""
    if extra_env:
        extra_env_string = "".join(f"{k}={v} " for k, v in extra_env.items())

    return f"{PROMPT}{extra_env_string}{cmd_str}"


def print_cli_output(
    cmd, output=None, error=None, error_code=None, extra_env=None
) -> None:
    """Same as above but print the full simulation of CLI execution, including output.

    Mostly used to print debug traces to user or in test results.
    """
    print(f"\n{format_cli(cmd, extra_env)}")
    if output:
        print(indent(output, INDENT))
    if error:
        print(indent(default_theme.error(error), INDENT))
    if error_code is not None:
        print(default_theme.error(f"{INDENT}Return code: {error_code}"))


def env_copy(extend: EnvVars | None = None) -> EnvVars | None:
    """Returns a copy of the current environment variables and eventually ``extend`` it.

    Mimics Python's original implementation by returning ``None`` if no ``extend``
    ``dict`` are added. See:
    https://github.com/python/cpython/blob/7b5b429adab4fe0fe81858fe3831f06adc2e2141/Lib/subprocess.py#L1648-L1649
    Environment variables are expected to be a ``dict`` of ``str:str``.
    """
    if isinstance(extend, dict):
        for k, v in extend.items():
            assert isinstance(k, str)
            assert isinstance(v, str)
    else:
        assert not extend
    env_copy: EnvVars | None = None
    if extend:
        # By casting to dict we make a copy and prevent the modification of the
        # global environment.
        env_copy = dict(os.environ)
        env_copy.update(extend)
    return env_copy


def run_cmd(*args, extra_env: EnvVars | None = None, print_output: bool = True):
    """Run a system command, print output and return results."""
    assert isinstance(args, tuple)
    process = subprocess.run(
        args,
        capture_output=True,
        encoding="utf-8",
        env=cast("subprocess._ENV", env_copy(extra_env)),
    )

    if print_output:
        print_cli_output(
            args,
            process.stdout,
            process.stderr,
            process.returncode,
            extra_env=extra_env,
        )

    return process.returncode, process.stdout, process.stderr

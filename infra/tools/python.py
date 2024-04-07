# Copyright 2024, Peter Birch, mailto:peter@intuity.io
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
from typing import ClassVar

from blockwork.context import Context
from blockwork.tools import Invocation, Require, Tool, Version

from .compilers import GCC


@Tool.register()
class Python(Tool):
    versions: ClassVar[list[Version]] = [
        Version(
            location=Tool.HOST_ROOT / "python" / "3.12.2",
            version="3.12.2",
            requires=[Require(GCC, "13.1.0")],
            paths={
                "PATH": [Tool.CNTR_ROOT / "bin"],
                "LD_LIBRARY_PATH": [Tool.CNTR_ROOT / "lib"],
            },
            default=True,
        ),
    ]

    @Tool.installer("Python")
    def install(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        vernum = version.version
        tool_dir = Path("/tools") / version.location.relative_to(Tool.HOST_ROOT)
        script = [
            f"wget --quiet https://www.python.org/ftp/python/{vernum}/Python-{vernum}.tgz",
            f"tar -xf Python-{vernum}.tgz",
            f"cd Python-{vernum}",
            f"./configure --enable-optimizations --with-ensurepip=install "
            f"--enable-shared --prefix={tool_dir.as_posix()}",
            "make -j4",
            "make install",
            "cd ..",
            f"rm -rf Python-{vernum} ./*.tgz*",
        ]
        return Invocation(
            version=version,
            execute="bash",
            args=["-c", " && ".join(script)],
            workdir=tool_dir,
        )


@Tool.register()
class PythonSite(Tool):
    versions: ClassVar[list[Version]] = [
        Version(
            location=Tool.HOST_ROOT / "python-site" / "3.12.2",
            version="3.12.2",
            env={"PYTHONUSERBASE": Tool.CNTR_ROOT},
            paths={
                "PATH": [Tool.CNTR_ROOT / "bin"],
                "PYTHONPATH": [Tool.CNTR_ROOT / "lib" / "python3.11" / "site-packages"],
            },
            requires=[Require(Python, "3.12.2")],
            default=True,
        ),
    ]

    @Tool.action("PythonSite")
    def run(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        return Invocation(version=version, execute="python3", args=args)

    @Tool.installer("PythonSite")
    def install(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        return Invocation(
            version=version,
            execute="python3",
            args=[
                "-m",
                "pip",
                "--no-cache-dir",
                "install",
                "-r",
                ctx.host_root / "infra" / "tools" / "pythonsite.txt",
            ],
            interactive=True,
            host=True,
        )

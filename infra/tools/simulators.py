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

from .compilers import GCC, Autoconf, Bison, CCache, Flex, Help2Man
from .objstore import from_objstore


@Tool.register()
class Verilator(Tool):
    versions: ClassVar[list[Version]] = [
        Version(
            location=Tool.HOST_ROOT / "verilator" / "5.014",
            version="5.014",
            env={
                "VERILATOR_BIN": "../../bin/verilator_bin",
                "VERILATOR_ROOT": Tool.CNTR_ROOT / "share" / "verilator",
            },
            paths={"PATH": [Tool.CNTR_ROOT / "bin"]},
            requires=[
                Require(Autoconf, "2.71"),
                Require(Bison, "3.8"),
                Require(CCache, "4.8.2"),
                Require(GCC, "13.1.0"),
                Require(Flex, "2.6.4"),
                Require(Help2Man, "1.49.3"),
            ],
            default=True,
        ),
    ]

    @Tool.action("Verilator")
    def run(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        return Invocation(version=version, execute="verilator", args=args)

    @Tool.installer("Verilator")
    @from_objstore
    def install(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        vernum = version.version
        tool_dir = Path("/tools") / version.location.relative_to(Tool.HOST_ROOT)
        script = [
            f"wget --quiet https://github.com/verilator/verilator/archive/refs/tags/v{vernum}.tar.gz",
            f"tar -xf v{vernum}.tar.gz",
            f"cd verilator-{vernum}",
            "autoconf",
            f"./configure --prefix={tool_dir.as_posix()}",
            "make -j4",
            "make install",
            "cd ..",
            f"rm -rf verilator-{vernum} ./*.tar.*",
        ]
        return Invocation(
            version=version,
            execute="bash",
            args=["-c", " && ".join(script)],
            workdir=tool_dir,
        )
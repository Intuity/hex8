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
class Curl(Tool):
    versions: ClassVar[list[Version]] = [
        Version(
            location=Tool.HOST_ROOT / "curl" / "8.7.1",
            version="8.7.1",
            requires=[Require(GCC, "13.1.0")],
            paths={
                "PATH": [Tool.CNTR_ROOT / "bin"],
                "LD_LIBRARY_PATH": [Tool.CNTR_ROOT / "lib"],
                "C_INCLUDE_PATH": [Tool.CNTR_ROOT / "include"],
                "CPLUS_INCLUDE_PATH": [Tool.CNTR_ROOT / "include"],
            },
            default=True,
        ),
    ]

    @Tool.installer("Curl")
    def install(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        vernum = version.version
        tool_dir = Path("/tools") / version.location.relative_to(Tool.HOST_ROOT)
        script = [
            f"wget --quiet https://curl.se/download/curl-{vernum}.tar.gz",
            f"tar -xf curl-{vernum}.tar.gz",
            f"cd curl-{vernum}",
            f"./configure --prefix={tool_dir.as_posix()} --with-openssl",
            "make -j4",
            "make install",
            "cd ..",
            f"rm -rf curl-{vernum} ./*.tar.gz*",
        ]
        return Invocation(
            version=version,
            execute="bash",
            args=["-c", " && ".join(script)],
            workdir=tool_dir,
        )


@Tool.register()
class Expat(Tool):
    versions: ClassVar[list[Version]] = [
        Version(
            location=Tool.HOST_ROOT / "expat" / "2.6.2",
            version="2.6.2",
            requires=[Require(GCC, "13.1.0")],
            paths={
                "PATH": [Tool.CNTR_ROOT / "bin"],
                "LD_LIBRARY_PATH": [Tool.CNTR_ROOT / "lib"],
                "C_INCLUDE_PATH": [Tool.CNTR_ROOT / "include"],
                "CPLUS_INCLUDE_PATH": [Tool.CNTR_ROOT / "include"],
            },
            default=True,
        ),
    ]

    @Tool.installer("Expat")
    def install(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        vernum = version.version
        tool_dir = Path("/tools") / version.location.relative_to(Tool.HOST_ROOT)
        script = [
            f"wget --quiet https://github.com/libexpat/libexpat/releases/download"
            f"/R_{vernum.replace('.', '_')}/expat-{vernum}.tar.gz",
            f"tar -xf expat-{vernum}.tar.gz",
            f"cd expat-{vernum}",
            f"./configure --prefix={tool_dir.as_posix()}",
            "make -j4",
            "make install",
            "cd ..",
            f"rm -rf expat-{vernum} ./*.tar.gz*",
        ]
        return Invocation(
            version=version,
            execute="bash",
            args=["-c", " && ".join(script)],
            workdir=tool_dir,
        )

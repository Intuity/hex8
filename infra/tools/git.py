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
from .libs import Curl, Expat


@Tool.register()
class Git(Tool):
    versions: ClassVar[list[Version]] = [
        Version(
            location=Tool.HOST_ROOT / "git" / "2.44.0",
            version="2.44.0",
            requires=[Require(GCC, "13.1.0"),
                      Require(Curl, "8.7.1"),
                      Require(Expat, "2.6.2")],
            paths={
                "PATH": [Tool.CNTR_ROOT / "bin"],
            },
            default=True,
        ),
    ]

    @Tool.installer("Git")
    def install(self, ctx: Context, version: Version, *args: list[str]) -> Invocation:
        vernum = version.version
        tool_dir = Path("/tools") / version.location.relative_to(Tool.HOST_ROOT)
        curl_root = ctx.container_tools / Curl().default.path_chunk
        expat_root = ctx.container_tools / Expat().default.path_chunk
        ldflags = f"-L{curl_root}/lib -L{expat_root}/lib -lcurl -lexpat"
        cppflags = f"-I{curl_root}/include -I{expat_root}/include"
        script = [
            f"wget --quiet https://www.kernel.org/pub/software/scm/git/git-{vernum}.tar.gz",
            f"tar -xf git-{vernum}.tar.gz",
            f"cd git-{vernum}",
            f"./configure --prefix={tool_dir.as_posix()} --with-curl={curl_root} "
            f"--with-openssl --with-expat={expat_root}",
            f"make -j4 LDFLAGS=\"{ldflags}\" CPPFLAGS=\"{cppflags}\"",
            "make install",
            "cd ..",
            f"rm -rf git-{vernum} ./*.tar.gz*",
        ]
        return Invocation(
            version=version,
            execute="bash",
            args=["-c", " && ".join(script)],
            workdir=tool_dir,
        )

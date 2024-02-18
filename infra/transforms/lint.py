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

from typing import ClassVar

from blockwork.build import Transform
from blockwork.tools import Tool

from ..interfaces.module import ModuleInterface
from ..tools.simulators import Verilator


class VerilatorLintTransform(Transform):
    tools: ClassVar[list[Tool]] = [Verilator]

    def __init__(self, module: ModuleInterface):
        super().__init__()
        self.bind_inputs(module=module)

    def execute(self, ctx, tools, iface):
        hdr_dirs = { x.parent for x in iface.module.headers }
        yield tools.verilator.get_action("run")(ctx,
                                                "--lint-only",
                                                "-Wall",
                                                *[f"+incdir+{x}" for x in hdr_dirs],
                                                *iface.module.packages,
                                                *iface.module.sources)

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

from collections.abc import Iterable

from blockwork.build.transform import Transform
from blockwork.common.checkeddataclasses import field
from blockwork.config import base

from ..interfaces.module import ModuleInterface
from ..transforms.lint import VerilatorLintTransform


class Module(base.Config):
    top: str
    headers: list[str] = field(default_factory=list)
    packages: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    transforms: list[Transform] = field(default_factory=list)

    def iter_config(self):
        yield from self.transforms

    def to_interface(self) -> ModuleInterface:
        return ModuleInterface(headers=map(self.api.path, self.headers),
                               packages=map(self.api.path, self.packages),
                               sources=map(self.api.path, self.sources))

    def iter_transforms(self) -> Iterable[Transform]:
        yield VerilatorLintTransform(module=self.to_interface())

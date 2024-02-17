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
from pathlib import Path

from blockwork.build.interface import Interface, MetaInterface
from blockwork.common.complexnamespaces import ReadonlyNamespace


class ModuleInterface(MetaInterface):
    def __init__(self,
                 headers: Iterable[Interface[Path]],
                 packages: Iterable[Interface[Path]],
                 sources: Iterable[Interface[Path]]) -> None:
        self.headers = list(headers)
        self.packages = list(packages)
        self.sources = list(sources)

    def resolve_meta(self, fn):
        return ReadonlyNamespace(headers=self.map(fn, self.headers),
                                 packages=self.map(fn, self.packages),
                                 sources=self.map(fn, self.sources))

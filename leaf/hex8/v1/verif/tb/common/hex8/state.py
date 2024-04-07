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

from enum import IntEnum, auto
from dataclasses import dataclass

from forastero import BaseTransaction

from .h8_pkg import Instruction


class Hex8MemoryOp(IntEnum):
    NOTHING = auto()
    LOAD = auto()
    STORE = auto()


@dataclass(kw_only=True)
class Hex8State(BaseTransaction):
    pc: int = 0
    op: Instruction = Instruction()
    areg: int = 0
    breg: int = 0
    memory: Hex8MemoryOp = Hex8MemoryOp.NOTHING
    address: int = 0
    data: int = 0

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

import packtype
from packtype import Constant, Scalar


@packtype.package()
class H8Pkg:
    OPCODE_W: Constant = 4


@packtype.enum(package=H8Pkg, width=H8Pkg.OPCODE_W)
class Opcode:
    LDAM: Constant = 0b0000
    LDBM: Constant = 0b0001
    STAM: Constant = 0b0010
    LDAC: Constant = 0b0011
    LDBC: Constant = 0b0100
    LDAP: Constant = 0b0101
    LDAI: Constant = 0b0110
    LDBI: Constant = 0b0111
    STAI: Constant = 0b1000
    BR: Constant = 0b1001
    BRZ: Constant = 0b1010
    BRN: Constant = 0b1011
    BRB: Constant = 0b1100
    ADD: Constant = 0b1101
    SUB: Constant = 0b1110
    PFIX: Constant = 0b1111


@packtype.struct(package=H8Pkg)
class Instruction:
    imm_u4: Scalar[4]
    op: Opcode

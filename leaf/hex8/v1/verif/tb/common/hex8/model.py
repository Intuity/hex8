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

from h8_pkg import Opcode, Instruction

from .state import Hex8State, Hex8MemoryOp


class Hex8Model:

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.pc = 0
        self.areg = 0
        self.breg = 0
        self.pfix = 0
        self.imem = {}
        self.dmem = {}

    def step(self) -> Hex8State:
        # Get instruction from memory
        op = Instruction._pt_unpack(self.imem.get(self.pc, 0))
        # Determine the fully prefixed constant
        oreg = (self.pfix << 4) | op.imm_u4
        self.pfix = 0
        # Execute
        next_pc = self.pc + 1
        mem_op = Hex8MemoryOp.NOTHING
        address = 0
        data = 0
        match op.op:
            # Load A from memory using immediate as address
            case Opcode.LDAM:
                self.areg = self.dmem.get(oreg, 0)
                mem_op = Hex8MemoryOp.LOAD
                address = oreg
                data = self.areg
            # Load B from memory using immediate as address
            case Opcode.LDBM:
                self.breg = self.dmem.get(oreg, 0)
                mem_op = Hex8MemoryOp.LOAD
                address = oreg
                data = self.breg
            # Store A to memory using immediate as address
            case Opcode.STAM:
                self.dmem[oreg] = self.areg
                mem_op = Hex8MemoryOp.STORE
                address = oreg
                data = self.areg
            # Load constant into A
            case Opcode.LDAC:
                self.areg = oreg
            # Load constant into B
            case Opcode.LDBC:
                self.breg = oreg
            # Load PC into A adding the immediate
            case Opcode.LDAP:
                self.areg = (self.pc + oreg) & 0xFF
            # Load A from memory based on address in A plus immediate offset
            case Opcode.LDAI:
                self.areg = self.dmem.get((self.areg + oreg) & 0xFF, 0)
                mem_op = Hex8MemoryOp.LOAD
                address = oreg
                data = self.areg
            # Load B from memory based on address in B plus immediate offset
            case Opcode.LDBI:
                self.breg = self.dmem.get((self.breg + oreg) & 0xFF, 0)
                mem_op = Hex8MemoryOp.LOAD
                address = oreg
                data = self.breg
            # Store A to memory at address held in B plus immediate offset
            case Opcode.STAI:
                self.dmem[(self.breg + oreg) & 0xFF] = self.areg
                mem_op = Hex8MemoryOp.STORE
                address = oreg
                data = self.areg
            # Branch unconditionally
            case Opcode.BR:
                next_pc = (self.pc + oreg) & 0xFF
            # Branch if A is 0
            case Opcode.BRZ:
                if self.areg == 0:
                    next_pc = (self.pc + oreg) & 0xFF
            # Branch if A is less than 0 (i.e. MSB set)
            case Opcode.BRN:
                if self.areg & 0x80:
                    next_pc = (self.pc + oreg) & 0xFF
            # Branch unconditonally to address held in B
            case Opcode.BRB:
                next_pc = self.breg
            # Add A and B and store into A
            case Opcode.ADD:
                self.areg = (self.areg + self.breg) & 0xFF
            # Subtract B from A and store into A
            case Opcode.SUB:
                self.areg = (self.areg - self.breg) & 0xFF
            # Store a prefix
            case Opcode.PFIX:
                self.pfix = op.imm_u4
        # Create state object
        state = Hex8State(pc=self.pc,
                          op=op,
                          areg=self.areg,
                          breg=self.breg,
                          memory=mem_op,
                          address=address,
                          data=data)
        # Update PC
        self.pc = next_pc
        # Generate state object
        return state

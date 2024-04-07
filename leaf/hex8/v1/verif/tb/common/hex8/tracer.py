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

import cocotb
from cocotb.handle import HierarchyObject, ModifiableObject
from forastero import BaseBench, BaseIO, BaseMonitor

from h8_pkg import Opcode, Instruction

from .state import Hex8State, Hex8MemoryOp


class Hex8Tracer(BaseMonitor):

    def __init__(self,
                 tb: BaseBench,
                 io: BaseIO,
                 clk: ModifiableObject,
                 rst: ModifiableObject,
                 core: HierarchyObject) -> None:
        super().__init__(tb, io, clk, rst)
        self.core = core
        cocotb.start_soon(self.trace())

    async def monitor(self, capture) -> None:
        fetch = None
        execute = None
        while True:
            # On reset, clear pipelined state
            if self.rst.value == 1:
                fetch = None
                execute = None
                continue

            # If a transaction was in execute, it is now committed
            if execute and execute.memory is Hex8MemoryOp.LOAD:
                execute.areg = int(self.core.i_dmem_rsp_data.areg)
                execute.breg = int(self.core.i_dmem_rsp_data.breg)
                execute.data = int(self.core.i_dmem_rsp_data.value)
                capture(execute)
                execute = None

            # If a transaction was in fetch, it is now executed
            if fetch:
                execute = fetch
                execute.op = Instruction._pt_unpack(int(self.core.i_imem_rsp_data.value))
                if self.core.o_dmem_req_valid.value == 1:
                    execute.address = int(self.core.o_dmem_req_addr.value)
                    if self.core.o_dmem_req_write.value == 1:
                        execute.memory = Hex8MemoryOp.STORE
                        execute.data = int(self.core.o_dmem_req_data.value)
                    else:
                        execute.memory = Hex8MemoryOp.LOAD
                fetch = None

            # If instruction request valid high, then fetch occurred
            if self.core.o_imem_req_valid.value == 1:
                fetch = Hex8State(pc=int(self.core.o_imem_req_addr.value))

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

from random import Random

from cocotb.handle import HierarchyObject
from forastero import BaseBench, IORole

from .common.byte_memory import (
    ByteMemoryIO,
    ByteMemoryRequestMonitor,
    ByteMemoryResponseDriver,
    ByteMemoryModel,
)
from .common.h8_model import Hex8Model


class Testbench(BaseBench):

    def __init__(self, dut: HierarchyObject) -> None:
        super().__init__(dut,
                         clk=dut.i_clk,
                         rst=dut.i_rst,
                         clk_drive=True,
                         clk_period=1,
                         clk_units="ns")
        # Instruction memory
        inst_io = ByteMemoryIO(self.dut, "inst", IORole.INITIATOR)
        self.register("inst_mon", ByteMemoryRequestMonitor(self, inst_io, self.clk, self.rst))
        self.register("inst_drv", ByteMemoryResponseDriver(self, inst_io, self.clk, self.rst))
        self.inst_mem = ByteMemoryModel(self.inst_mon,
                                        self.inst_drv,
                                        Random(self.random.random()),
                                        self.fork_log("model", "inst_mem"))
        # Data memory
        data_io = ByteMemoryIO(self.dut, "data", IORole.INITIATOR)
        self.register("data_mon", ByteMemoryRequestMonitor(self, data_io, self.clk, self.rst))
        self.register("data_drv", ByteMemoryResponseDriver(self, data_io, self.clk, self.rst))
        self.data_mem = ByteMemoryModel(self.data_mon,
                                        self.data_drv,
                                        Random(self.random.random()),
                                        self.fork_log("model", "data_mem"))

    async def initialise(self) -> None:
        await super().initialise()
        self.inst_mem.reset()
        self.data_mem.reset()

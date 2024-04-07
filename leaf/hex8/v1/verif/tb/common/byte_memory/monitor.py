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

from cocotb.triggers import RisingEdge
from forastero import BaseMonitor

from .transaction import ByteMemoryRequest, ByteMemoryResponse


class ByteMemoryRequestMonitor(BaseMonitor):

    async def monitor(self, capture) -> None:
        while True:
            await RisingEdge(self.clk)
            if self.rst.value != 0:
                continue
            if self.io.get("req_valid", 1):
                capture(ByteMemoryRequest(address=self.io.get("req_addr", 0),
                                          data=self.io.get("req_data", 0),
                                          write=self.io.get("req_write", 0) != 0))


class ByteMemoryResponseMonitor(BaseMonitor):

    async def monitor(self, capture) -> None:
        while True:
            await RisingEdge(self.clk)
            if self.rst.value != 0:
                continue
            if self.io.get("req_valid", 1):
                await RisingEdge(self.clk)
                if self.rst.value != 0:
                    continue
                capture(ByteMemoryResponse(data=self.io.get("rsp_data", 0)))

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
from forastero import BaseDriver

from .transaction import ByteMemoryRequest, ByteMemoryResponse


class ByteMemoryRequestDriver(BaseDriver):

    async def drive(self, obj: ByteMemoryRequest) -> None:
        self.io.set("req_addr", obj.address)
        self.io.set("req_write", [0, 1][obj.write])
        self.io.set("req_data", obj.data)
        self.io.set("req_valid", 1)
        await RisingEdge(self.clk)
        self.io.set("req_valid", 0)


class ByteMemoryResponseDriver(BaseDriver):

    async def drive(self, obj: ByteMemoryResponse) -> None:
        self.io.set("rsp_data", obj.data)
        await RisingEdge(self.clk)

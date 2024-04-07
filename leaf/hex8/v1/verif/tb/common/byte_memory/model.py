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

from cocotb.log import SimLog
from forastero import MonitorEvent

from .driver import ByteMemoryResponseDriver
from .monitor import ByteMemoryRequestMonitor
from .transaction import ByteMemoryRequest, ByteMemoryResponse


class ByteMemoryModel:

    def __init__(self,
                 request: ByteMemoryRequestMonitor,
                 response: ByteMemoryResponseDriver,
                 random: Random,
                 log: SimLog) -> None:
        # Take references
        self._request = request
        self._response = response
        self._random = random
        self._log = log
        # Create memory storage
        self._memory = {}
        # Subscribe to requests
        self._request.subscribe(MonitorEvent.CAPTURE, self._service)

    def reset(self) -> None:
        self._memory.clear()

    def write(self, address: int, data: int) -> None:
        self._memory[address] = data

    def read(self, address: int) -> int:
        if address not in self._memory:
            self._memory[address] = self._random.getrandbits(8)
        return self._memory[address]

    def _service(self,
                 component: ByteMemoryRequestMonitor,
                 event: MonitorEvent,
                 transaction: ByteMemoryRequest) -> None:
        assert component is self._request
        assert event is MonitorEvent.CAPTURE
        if transaction.write:
            self.write(transaction.address, transaction.data)
            self._response.enqueue(ByteMemoryResponse())
        else:
            self._response.enqueue(ByteMemoryResponse(
                data=self.read(transaction.address)
            ))

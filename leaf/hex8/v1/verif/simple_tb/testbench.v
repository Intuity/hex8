// Copyright 2024, Peter Birch, mailto:peter@intuity.io
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module testbench;

// =============================================================================
// Generate Clock
// =============================================================================

reg clk;

// Start the clock initially high
initial clk = 1'd1;

// Every 1ns toggle the clock (generates a 500MHz clock)
always #1ns clk = ~clk;

// =============================================================================
// Generate Reset
// =============================================================================

reg rst;

initial begin
    // Start reset high
    rst = 1'd1;
    // Wait for 20 clock cycles
    repeat (20) @(posedge clk);
    // Drop reset
    rst = 1'd0;
end

// =============================================================================
// Signals
// =============================================================================

// Instruction Memory
wire [7:0] imem_req_addr, imem_rsp_data;
wire       imem_req_valid;

// Data Memory
wire [7:0] dmem_req_addr, dmem_req_data, dmem_rsp_data;
wire       dmem_req_write, dmem_req_valid;

// =============================================================================
// DUT
// =============================================================================

h8_core u_dut (
      .i_clk            ( clk            )
    , .i_rst            ( rst            )
    // Instruction Memory
    , .o_imem_req_addr  ( imem_req_addr  )
    , .o_imem_req_valid ( imem_req_valid )
    , .i_imem_rsp_data  ( imem_rsp_data  )
    // Data Memory
    , .o_dmem_req_addr  ( dmem_req_addr  )
    , .o_dmem_req_data  ( dmem_req_data  )
    , .o_dmem_req_write ( dmem_req_write )
    , .o_dmem_req_valid ( dmem_req_valid )
    , .i_dmem_rsp_data  ( dmem_rsp_data  )
);

// =============================================================================
// Memories
// =============================================================================

ram_1rw u_imem (
      .i_clk       ( clk            )
    , .i_rst       ( rst            )
    , .i_req_addr  ( imem_req_addr  )
    , .i_req_data  ( 8'd0           )
    , .i_req_write ( 1'd0           )
    , .i_req_valid ( imem_req_valid )
    , .o_rsp_data  ( imem_rsp_data  )
);

ram_1rw u_dmem (
      .i_clk       ( clk            )
    , .i_rst       ( rst            )
    , .i_req_addr  ( dmem_req_addr  )
    , .i_req_data  ( dmem_req_data  )
    , .i_req_write ( dmem_req_write )
    , .i_req_valid ( dmem_req_valid )
    , .o_rsp_data  ( dmem_rsp_data  )
);

endmodule : testbench

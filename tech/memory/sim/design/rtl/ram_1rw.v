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

module ram_1rw (
      input  wire       i_clk
    , input  wire       i_rst
    , input  wire [7:0] i_req_addr
    , input  wire [7:0] i_req_data
    , input  wire       i_req_write
    , input  wire       i_req_valid
    , output reg  [7:0] o_rsp_data
);

reg [7:0] data_q [255:0];

// Handle writes
always @(posedge i_clk, posedge i_rst) begin
    if (i_rst) begin
        for (integer idx = 0; idx < 256; idx++)
            data_q[idx] <= 8'd0;
    end else begin
        for (integer idx = 0; idx < 256; idx++)
            data_q[idx] <= (i_req_valid &&
                            i_req_write &&
                            (i_req_addr == 8'(idx))) ? i_req_data
                                                     : data_q[idx];
    end
end

// Handle reads
always @(posedge i_clk, posedge i_rst) begin
    if (i_rst) o_rsp_data <= 8'd0;
    else       o_rsp_data <= (i_req_valid && !i_req_write) ? data_q[i_req_addr]
                                                           : o_rsp_data;
end

endmodule : ram_1rw

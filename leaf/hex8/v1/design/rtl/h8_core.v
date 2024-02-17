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

module h8_core (
      input  wire       i_clk
    , input  wire       i_rst
    // Instruction Memory
    , output wire [7:0] o_imem_req_addr
    , output wire       o_imem_req_valid
    , input  wire [7:0] i_imem_rsp_data
    // Data Memory
    , output wire [7:0] o_dmem_req_addr
    , output wire [7:0] o_dmem_req_data
    , output wire       o_dmem_req_write
    , output wire       o_dmem_req_valid
    , input  wire [7:0] i_dmem_rsp_data
);

// =============================================================================
// Signals
// =============================================================================

// Fetch
reg [7:0] pc_fetch_d, pc_fetch_q;
reg       flush_q;

// Execution
// - PC & qualifier
wire [7:0] pc;
wire       valid;
// - Operator/immediate separation
wire [3:0] op, imm_u4;
wire [7:0] imm_u8;
// - Decode
wire       is_ldam, is_ldbm, is_stam, is_ldac, is_ldbc, is_ldap, is_ldai,
           is_ldbi, is_stai, is_br, is_brz, is_brn, is_brb, is_add, is_sub,
           is_pfix;
// - Operand muxing
wire [7:0] op_0, op_1;
// - ALU
wire [7:0] result;
// - Data memory loads & stores
wire       dmem_ld_a, dmem_ld_b, dmem_st_a;
reg        ld_a_pend_q, ld_b_pend_q;
// - Branching
wire       take_branch;
wire [7:0] target_pc;

// Register file
reg [7:0] areg, areg_d, areg_q,
          breg, breg_d, breg_q;
reg [3:0] pfix_d, pfix_q;

// =============================================================================
// Fetch
// =============================================================================

// Maintain the fetch PC
assign pc_fetch_d = take_branch ? target_pc : { pc_fetch_q + 8'd1 };

// Drive instruction memory interface
// NOTE: As pipeline cannot be backpressured, valid driven constantly high
assign o_imem_req_addr  = pc_fetch_q;
assign o_imem_req_valid = 1'd1;

// NOTE: flush_q tracks when the pipeline is invalidated, it only needs to be
//       high on the very first cycle before any instruction is fetched. Due to
//       the shallow pipeline depth, branch targets can be immediately fetched
//       without flushing the pipe.
always @(posedge i_clk, posedge i_rst) begin
    if (i_rst) begin
        pc_fetch_q <= 8'd0;
        flush_q    <= 1'd1;
    end else begin
        pc_fetch_q <= pc_fetch_d;
        flush_q    <= 1'd0;
    end
end

// =============================================================================
// PC & Qualifier
// =============================================================================

// Adopt PC from pipelined fetch address
assign pc = pc_fetch_q;

// Qualify instruction with the pipelined flush state
assign valid = !flush_q;

// =============================================================================
// Operator/Immediate Separation
// =============================================================================

// Separate instruction into the operator and 4-bit immediate
assign {op, imm_u4} = i_imem_rsp_data;

// Extend the 4-bit immediate with the prefix
assign imm_u8 = {pfix_q, imm_u4};

// =============================================================================
// Decode
// =============================================================================

assign is_ldam = (op == 4'b0000);
assign is_ldbm = (op == 4'b0001);
assign is_stam = (op == 4'b0010);
assign is_ldac = (op == 4'b0011);
assign is_ldbc = (op == 4'b0100);
assign is_ldap = (op == 4'b0101);
assign is_ldai = (op == 4'b0110);
assign is_ldbi = (op == 4'b0111);
assign is_stai = (op == 4'b1000);
assign is_br   = (op == 4'b1001);
assign is_brz  = (op == 4'b1010);
assign is_brn  = (op == 4'b1011);
assign is_brb  = (op == 4'b1100);
assign is_add  = (op == 4'b1101);
assign is_sub  = (op == 4'b1110);
assign is_pfix = (op == 4'b1111);

// =============================================================================
// Capture Memory Read Response
// =============================================================================

assign areg = ld_a_pend_q ? i_dmem_rsp_data : areg_q;
assign breg = ld_b_pend_q ? i_dmem_rsp_data : breg_q;

// =============================================================================
// Operand Muxing
// =============================================================================

// First operand
assign op_0 = (
    // LDAI, LDBI, STAI, ADD & SUB -> areg
    (|{is_ldai, is_ldbi, is_stai, is_add, is_sub}) ? areg :
    // LDAP, BR, BRZ & BRN -> PC
    (|{is_ldap, is_br,   is_brz,  is_brn        }) ? pc
    // Otherwise -> 0
                                                   : 8'd0
);

// Second operand
assign op_1 = (
    // BRB, ADD & SUB -> breg
    (|{is_brb, is_add, is_sub}) ? breg
    // Otherwise -> oreg
                                : imm_u8
);

// =============================================================================
// ALU
// =============================================================================

assign result = is_sub ? { op_0 - op_1 }
                       : { op_0 + op_1 };

// =============================================================================
// Load / Store
// =============================================================================

// Detect loads/stores from/to memory
assign dmem_ld_a = is_ldam || is_ldai;
assign dmem_ld_b = is_ldbm || is_ldbi;
assign dmem_st_a = is_stam || is_stai;

// Drive data memory interface
// - Address always comes from the ALU
assign o_dmem_req_addr  = result;
// - Write data is taken from areg (for both STAM and STAI)
assign o_dmem_req_data  = areg;
// - Write flag is raised for STAM and STAI
assign o_dmem_req_write = dmem_st_a;
// - Valid raised for all load/store operations
assign o_dmem_req_valid = valid && |{dmem_ld_a, dmem_ld_b, dmem_st_a};

// Remember pending loads/stores
always @(posedge i_clk, posedge i_rst) begin
    if (i_rst) begin
        ld_a_pend_q <= 'd0;
        ld_b_pend_q <= 'd0;
    end else begin
        ld_a_pend_q <= dmem_ld_a;
        ld_b_pend_q <= dmem_ld_b;
    end
end

// =============================================================================
// Branching
// =============================================================================

// Take branch when...
assign take_branch = (is_br                   ) || // BR: Unconditional
                     (is_brz && (areg == 8'd0)) || // BRZ: areg is zero
                     (is_brn && areg[7]       ) || // BRN: areg is negative
                     (is_brb                  );   // BRB: Unconditional

// Decide the target PC
// NOTE: BRB adopts the value from breg, while all other branches are relative
//       to the current PC and hence the ALU result is taken
assign target_pc = is_brb ? breg : result;

// =============================================================================
// Register File
// =============================================================================

// Determine value to commit for areg
assign areg_d = (
    // LDAC, LDAP, ADD & SUB: Adopt the ALU result
    (valid && |{is_ldac, is_ldap, is_add, is_sub}) ? result :
    // Pending load to A: Adopt the data memory response
    (ld_a_pend_q                                 ) ? i_dmem_rsp_data
    // Otherwise preserve the current value
                                                   : areg_q
);

// Determine the value to commit for breg
assign breg_d = (
    // LDBC: Adopt the ALU result
    (valid && is_ldbc) ? result :
    // Pending load to B: Adopt the data memory response
    ld_b_pend_q        ? i_dmem_rsp_data
    // Otherwise preserve the current value
                       : breg_q
);

// Capture prefix
// NOTE: Always return to 0 after one cycle
assign pfix_d = is_pfix ? imm_u4 : 'd0;

always @(posedge i_clk, posedge i_rst) begin
    if (i_rst) begin
        areg_q <= 8'd0;
        breg_q <= 8'd0;
        pfix_q <= 4'd0;
    end else begin
        areg_q <= areg_d;
        breg_q <= breg_d;
        pfix_q <= pfix_d;
    end
end

endmodule : h8_core

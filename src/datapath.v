module datapath (
    input [23:0] x,
    input [23:0] y,
    output [23:0] q,
    output carry,
    input sel_rx,
    input sel_ri,
    input en_y,
    input en_r,
    input en_shift,
    input clk,
    input rst
);

wire [24:0] mux_rx_out, mux_ri_out, reg_r_out, reg_y_out, sub_out, internal_y;
wire not_internal_carry, internal_carry;

// The r X multiplexer
assign mux_rx_out = (sel_rx == 1'b0) ? {mux_ri_out[23:0], 1'b0} : {1'b0, x};

// The remainder register
fullreg #(.N(25)) regr (
    .clk(clk),
    .rst(rst),
    .clr(1'b0),
    .en(en_r),
    .d(mux_rx_out),
    .q(reg_r_out)
);

// The y register
assign internal_y = {1'b0, y};
fullreg #(.N(25)) regy (
    .clk(clk),
    .rst(rst),
    .clr(1'b0),
    .en(en_y),
    .d(internal_y),
    .q(reg_y_out)
);

// The subtractor
assign sub_out = reg_r_out - reg_y_out;
assign internal_carry = sub_out[24];
assign not_internal_carry = ~internal_carry;
assign carry = internal_carry;

// The residue multiplexer
assign mux_ri_out = (sel_ri == 1'b0) ? reg_r_out : sub_out;

// The shift register
shift_reg #(.N(24)) shift_reg0 (
    .clk(clk),
    .rst(rst),
    .clr(1'b0),
    .en(en_shift),
    .serial_in(not_internal_carry),
    .q(q)
);

endmodule
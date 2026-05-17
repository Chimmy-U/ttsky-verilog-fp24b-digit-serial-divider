module digit_serial_divider_core (
    input [23:0] x,
    input [23:0] y,
    output [23:0] q,
    input start,
    output done,
    input clk,
    input rst
);

wire sel_rx, sel_ri, en_y, en_r, en_shift, carry;

datapath datapath0 (
    .x(x),
    .y(y),
    .q(q),
    .carry(carry),
    .sel_rx(sel_rx),
    .sel_ri(sel_ri),
    .en_y(en_y),
    .en_r(en_r),
    .en_shift(en_shift),
    .clk(clk),
    .rst(rst)
);

controlpath controlpath0 (
    .start(start),
    .carry(carry),
    .sel_rx(sel_rx),
    .sel_ri(sel_ri),
    .en_y(en_y),
    .en_r(en_r),
    .en_shift(en_shift),
    .done(done),
    .clk(clk),
    .rst(rst)
);

endmodule
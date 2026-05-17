module controlpath (
    input clk,
    input rst,
    output sel_rx,
    output sel_ri,
    output en_y,
    output en_r,
    output en_shift,
    input carry,
    input start,
    output  done
);

wire ovf, en_counter, clr_counter;
wire [4:0] counter_out, adder_out;

// Instantiate the FSM
fsm fsm0 (
    .clk(clk),
    .rst(rst),
    .sel_rx(sel_rx),
    .sel_ri(sel_ri),
    .en_y(en_y),
    .en_r(en_r),
    .en_shift(en_shift),
    .en_counter(en_counter),
    .clr_counter(clr_counter),
    .ovf(ovf),
    .carry(carry),
    .start(start)
);

// Instantiate the counter register
fullreg #(.N(5)) regr (
    .clk(clk),
    .rst(rst),
    .clr(clr_counter),
    .en(en_counter),
    .d(adder_out),
    .q(counter_out)
);

// The counter adder
assign adder_out = counter_out + 1;

// The comparator
assign ovf = (counter_out == 24) ? 1'b1 : 1'b0;
    
assign done = ovf;

endmodule
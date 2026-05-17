`default_nettype none

module tt_um_digit_serial_divider (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);


digit_serial_divider unit_digit_serial_divider(
    .rst(~rst_n),
    .clk(clk),
    .x(ui_in[0]), // Dividend X
    .y(ui_in[1]), // Divisor Y
    .start(ui_in[2]), // START signal
    
    .q(uo_out[0]), // Quotient Q
    .done(uo_out[1]) // DONE signal
);

wire _unused = &{ena, uio_in, ui_in[7:3],1'b0};

assign uio_out = 8'bz;
assign uio_oe = 8'b0;
assign uo_out[7:2] = 6'b0;

endmodule
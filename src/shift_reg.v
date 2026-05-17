module shift_reg #(
    parameter N = 8
)(
    input clk,
    input en,
    input rst,
    input clr,
    input serial_in,
    output [N-1:0] q
);

reg [N-1:0] internal_q;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        internal_q <= 0;
    end
    else if (en) begin
        if (clr) begin
            internal_q <= 0;
        end
        else begin
            internal_q <= {internal_q[N-2:0], serial_in};
        end
    end
end

assign q = internal_q;

endmodule
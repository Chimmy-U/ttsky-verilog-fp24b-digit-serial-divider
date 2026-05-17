module fsm (
    input clk,
    input rst,
    output reg sel_rx,
    output reg sel_ri,
    output reg en_y,
    output reg en_r,
    output reg en_shift,
    output reg en_counter,
    output reg clr_counter,
    input ovf,
    input carry,
    input start
);

localparam start_state=2'b00;
localparam compute_state=2'b01;
localparam counter_state=2'b10;

reg [1:0] state;

// Next state logic and state register
always @(posedge clk or posedge rst) begin
    if (rst) begin
        state <= start_state;
    end
    else begin
        case (state)
            start_state: begin
                if (start)
                    state <= compute_state;
                else
                    state <= start_state;
            end
            compute_state: begin
                state <= counter_state;
            end
            counter_state: begin
                if (!ovf)
                    state <= compute_state;
                else
                    state <= start_state;
            end
            default: state <= start_state;
        endcase
    end
end

// Output logic
always @(*) begin
    case (state)
        start_state: begin
            sel_ri = 1'b0;
            en_shift = 1'b0;
            if (start) begin
                clr_counter = 1'b1;
                en_counter = 1'b1;
                en_y = 1'b1;
                en_r = 1'b1;
                sel_rx = 1'b1;
            end
            else begin
                clr_counter = 1'b0;
                en_counter = 1'b0;
                en_y = 1'b0;
                en_r = 1'b0;
                sel_rx = 1'b0;
            end
        end
        
        compute_state: begin
            en_shift = 1'b1;
            en_r = 1'b1;
            clr_counter = 1'b0;
            en_counter = 1'b1;
            en_y = 1'b0;
            sel_rx = 1'b0;
            sel_ri = (carry == 1'b0) ? 1'b1 : 1'b0;
        end
        
        counter_state: begin
            en_shift = 1'b0;
            en_r = 1'b0;
            clr_counter = 1'b0;
            en_counter = 1'b0;
            en_y = 1'b0;
            sel_rx = 1'b0;
            sel_ri = 1'b0;
        end
        
        default: begin
            en_shift = 1'b0;
            en_r = 1'b0;
            en_y = 1'b0;
            sel_rx = 1'b0;
            sel_ri = 1'b0;
            clr_counter = 1'b0;
            en_counter = 1'b0;
        end
    endcase
end

endmodule

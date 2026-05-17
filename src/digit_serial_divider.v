module digit_serial_divider (
    input  wire x,
    input  wire y,
    input  wire start,
    input  wire clk,
    input  wire rst,
    output wire q,
    output reg  done
);

    localparam WIDTH = 24;

    localparam [2:0]
        S_IDLE    = 3'd0,
        S_LOAD    = 3'd1,
        S_RUN     = 3'd2,
        S_CAPTURE = 3'd3,
        S_OUT     = 3'd4;

    reg [2:0]  state;
    reg [4:0]  load_count;
    reg [4:0]  out_count;

    reg [23:0] x_buf;
    reg [23:0] y_buf;
    reg [23:0] q_buf;

    reg  core_start;
    reg  core_done_d;
    wire core_done;
    wire [23:0] q_core;

    digit_serial_divider_core u_core (
        .x     (x_buf),
        .y     (y_buf),
        .q     (q_core),
        .start (core_start),
        .done  (core_done),
        .clk   (clk),
        .rst   (rst)
    );

    assign q = q_buf[0];

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state       <= S_IDLE;
            load_count  <= 5'd0;
            out_count   <= 5'd0;
            x_buf       <= 24'd0;
            y_buf       <= 24'd0;
            q_buf       <= 24'd0;
            core_start  <= 1'b0;
            core_done_d <= 1'b0;
            done        <= 1'b0;
        end else begin
            core_start  <= 1'b0;
            core_done_d <= core_done;

            case (state)
                S_IDLE: begin
                    done <= 1'b0;
                    if (start) begin
                        x_buf[0]    <= x;
                        y_buf[0]    <= y;
                        load_count  <= 5'd1;
                        state       <= S_LOAD;
                    end
                end

                S_LOAD: begin
                    x_buf[load_count] <= x;
                    y_buf[load_count] <= y;

                    if (load_count == WIDTH-1) begin
                        core_start <= 1'b1;
                        state      <= S_RUN;
                    end else begin
                        load_count <= load_count + 1'b1;
                    end
                end

                S_RUN: begin
                    if (core_done && !core_done_d) begin
                        state <= S_CAPTURE;
                    end
                end

                S_CAPTURE: begin
                    q_buf     <= q_core;
                    out_count <= 5'd0;
                    done      <= 1'b1;
                    state     <= S_OUT;
                end

                S_OUT: begin
                    done <= 1'b1;

                    if (out_count == WIDTH-1) begin
                        done  <= 1'b0;
                        state <= S_IDLE;
                    end else begin
                        q_buf     <= {1'b0, q_buf[23:1]};
                        out_count <= out_count + 1'b1;
                    end
                end

                default: begin
                    state <= S_IDLE;
                    done  <= 1'b0;
                end
            endcase
        end
    end

endmodule
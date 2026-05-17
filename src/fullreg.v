// Parameterizable register with enable and asynchronous reset
module fullreg #(  parameter N = 16 )(
    input [N-1:0] d,
    output reg [N-1:0] q,
    input clk,
    input en,
    input clr, // sync with clock signal
    input rst  //async (connected to button i.e.)
    );
   

      
always @(posedge clk,posedge rst) begin
    if(rst)
        q<=0;
    else    
    if(en==1)begin
        if(clr)
            q<=0;
        else
            q<=d;
    end
end
    
endmodule
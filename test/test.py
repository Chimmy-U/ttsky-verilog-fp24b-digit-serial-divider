# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles

WIDTH = 24
FRAC_BITS = 23
MASK = (1 << WIDTH) - 1


def float_to_fixed(value: float) -> int:
    """Convert a real value to 24-bit fixed-point with 23 fractional bits."""
    return int(round(value * (1 << FRAC_BITS))) & MASK


def fixed_to_float(value: int) -> float:
    """Convert a 24-bit fixed-point integer back to real."""
    return value / float(1 << FRAC_BITS)


def set_inputs(dut, x_bit: int, y_bit: int, start_bit: int) -> None:
    """Drive ui_in[0]=x, ui_in[1]=y, ui_in[2]=start."""
    dut.ui_in.value = (x_bit & 1) | ((y_bit & 1) << 1) | ((start_bit & 1) << 2)


async def reset_dut(dut):
    """Apply reset and initialize inputs."""
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def send_serial_operands(dut, x_word: int, y_word: int):
    """
    Send 24-bit operands serially, LSB first, while start is high.
    Matches the behavior of the Verilog testbench.
    """
    # Present bit 0 before the first active clock edge.
    await FallingEdge(dut.clk)
    set_inputs(dut, (x_word >> 0) & 1, (y_word >> 0) & 1, 1)

    # Load bits 1..23
    for i in range(1, WIDTH):
        await FallingEdge(dut.clk)
        set_inputs(dut, (x_word >> i) & 1, (y_word >> i) & 1, 1)

    # Deassert start after the 24-bit load is complete.
    await FallingEdge(dut.clk)
    set_inputs(dut, 0, 0, 0)

    # Give one cycle for the wrapper/core to move from LOAD to RUN.
    await RisingEdge(dut.clk)


async def receive_serial_q(dut) -> int:
    """
    Wait for done and capture 24 quotient bits serially, LSB first.
    The Verilog testbench samples on negedge; here we sample on FallingEdge.
    """
    # Wait until DONE goes high.
    while int(dut.uo_out.value[1]) == 0:
        await RisingEdge(dut.clk)

    q_word = 0

    for i in range(WIDTH):
        await FallingEdge(dut.clk)
        q_bit = int(dut.uo_out.value[0]) & 1
        q_word |= (q_bit << i)

    # Wait until DONE returns low before allowing another operation.
    while int(dut.uo_out.value[1]) == 1:
        await RisingEdge(dut.clk)

    return q_word


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Clock: 10 us period, as in the provided template
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut._log.info("Reset")
    await reset_dut(dut)

    dut._log.info("Test project behavior")

    # Example vector from the Verilog testbench
    x_real = 1.789634233478
    y_real = 1.974231473301

    x_word = float_to_fixed(x_real)
    y_word = float_to_fixed(y_real)

    await send_serial_operands(dut, x_word, y_word)
    q_word = await receive_serial_q(dut)

    # Expected quotient in real values
    expected_real = x_real / y_real
    expected_word = float_to_fixed(expected_real)

    dut._log.info(
        f"X = {x_real}, Y = {y_real}, expected q ≈ {expected_real:.12f}"
    )
    dut._log.info(
        f"Captured q_word = 0x{q_word:06X}, as real ≈ {fixed_to_float(q_word):.12f}"
    )

    # Allow a small tolerance in fixed-point LSBs
    assert abs(q_word - expected_word) <= 2, (
        f"Mismatch: captured=0x{q_word:06X}, expected=0x{expected_word:06X}"
    )

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer

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
    """
    Reset active-low in the wrapper.
    Equivalent to rst asserted for 100 ns in the original testbench.
    At 50 MHz, 100 ns = 5 cycles.
    """
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = 0

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def send_serial_operands(dut, x_word: int, y_word: int):
    """
    Send 24-bit operands serially, LSB first, while start is high.
    Matches the Verilog testbench behavior.
    """
    await FallingEdge(dut.clk)
    set_inputs(dut, (x_word >> 0) & 1, (y_word >> 0) & 1, 1)

    for i in range(1, WIDTH):
        await FallingEdge(dut.clk)
        set_inputs(dut, (x_word >> i) & 1, (y_word >> i) & 1, 1)

    await FallingEdge(dut.clk)
    set_inputs(dut, 0, 0, 0)

    # Give the DUT one edge to transition from LOAD to RUN
    await RisingEdge(dut.clk)


async def receive_serial_q(dut) -> int:
    """
    Receive 24 quotient bits serially, LSB first.

    This version is more robust for GDS:
    - wait until done becomes high
    - wait a small time for the gate-level netlist to settle
    - after each falling edge, wait again before sampling q
    """
    while int(dut.uo_out.value[1]) == 0:
        await RisingEdge(dut.clk)

    # Let done/q settle in gate-level simulation
    await Timer(1, units="ns")

    q_word = 0

    for i in range(WIDTH):
        await FallingEdge(dut.clk)
        await Timer(1, units="ns")   # allow q to settle after the edge
        q_bit = int(dut.uo_out.value[0]) & 1
        q_word |= (q_bit << i)

    while int(dut.uo_out.value[1]) == 1:
        await RisingEdge(dut.clk)

    return q_word


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # 50 MHz clock => 20 ns period
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    dut._log.info("Reset")
    await reset_dut(dut)

    dut._log.info("Test 1.5 / 1.0")

    x_real = 1.5
    y_real = 1.0

    x_word = float_to_fixed(x_real)
    y_word = float_to_fixed(y_real)

    dut._log.info(f"x_word = 0x{x_word:06X}")
    dut._log.info(f"y_word = 0x{y_word:06X}")

    await send_serial_operands(dut, x_word, y_word)
    q_word = await receive_serial_q(dut)

    expected_real = x_real / y_real
    expected_word = float_to_fixed(expected_real)

    dut._log.info(f"expected_real = {expected_real:.12f}")
    dut._log.info(f"captured q_word = 0x{q_word:06X}")
    dut._log.info(f"captured real   = {fixed_to_float(q_word):.12f}")
    dut._log.info(f"expected q_word = 0x{expected_word:06X}")

    assert q_word == expected_word, (
        f"Mismatch: captured=0x{q_word:06X}, expected=0x{expected_word:06X}"
    )

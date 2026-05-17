# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, ReadOnly, Timer
from cocotb.result import TestFailure

WIDTH = 24
FRAC_BITS = 23
MASK = (1 << WIDTH) - 1

# Ajusta esto solo si en GDS el resultado queda corrido 1 ciclo adicional.
# 0 = comportamiento normal
# 1 = esperar un ciclo extra después de done antes de capturar q
EXTRA_DONE_LATENCY = 0

# Tiempo pequeño para dejar que se propaguen las compuertas en GDS.
# 1 ns suele funcionar bien; si hace falta, prueba 2 ns.
SETTLE_NS = 1


def float_to_fixed(value: float) -> int:
    """Convierte real a punto fijo Q1.23 de 24 bits."""
    return int(round(value * (1 << FRAC_BITS))) & MASK


def fixed_to_float(value: int) -> float:
    """Convierte Q1.23 de 24 bits a real."""
    return value / float(1 << FRAC_BITS)


def set_inputs(dut, x_bit: int, y_bit: int, start_bit: int) -> None:
    """
    Mapea:
      ui_in[0] = x
      ui_in[1] = y
      ui_in[2] = start
    """
    dut.ui_in.value = (x_bit & 1) | ((y_bit & 1) << 1) | ((start_bit & 1) << 2)


async def settle():
    """
    Espera un tiempo pequeño y luego entra a ReadOnly para leer señales ya estables.
    Esto ayuda mucho en GDS.
    """
    await Timer(SETTLE_NS, unit="ns")
    await ReadOnly()


async def reset_dut(dut):
    dut.ena.value = 1
    dut.uio_in.value = 0
    dut.ui_in.value = 0

    # Reset activo en bajo
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    await settle()

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    await settle()


async def send_serial_operands(dut, x_word: int, y_word: int):
    """
    Envía operandos seriales LSB-first mientras start=1.
    Replica la intención del testbench Verilog, pero con estabilización.
    """
    await FallingEdge(dut.clk)
    set_inputs(dut, (x_word >> 0) & 1, (y_word >> 0) & 1, 1)
    await settle()

    for i in range(1, WIDTH):
        await FallingEdge(dut.clk)
        set_inputs(dut, (x_word >> i) & 1, (y_word >> i) & 1, 1)
        await settle()

    await FallingEdge(dut.clk)
    set_inputs(dut, 0, 0, 0)
    await settle()


async def wait_done_high(dut):
    """
    Espera hasta que done=1.
    Se muestrea después de RisingEdge + settle para evitar leer done antes de tiempo.
    """
    while True:
        await RisingEdge(dut.clk)
        await settle()
        if int(dut.uo_out.value[1]) == 1:
            return


async def receive_serial_q(dut) -> int:
    """
    Captura el cociente serial LSB-first:
      - espera done=1
      - opcionalmente espera un ciclo extra si GDS lo requiere
      - captura 24 bits en cada negedge con asentamiento
      - espera done=0 al final
    """
    await wait_done_high(dut)

    for _ in range(EXTRA_DONE_LATENCY):
        await FallingEdge(dut.clk)
        await settle()

    q_word = 0

    for i in range(WIDTH):
        await FallingEdge(dut.clk)
        await settle()

        q_bit = int(dut.uo_out.value[0]) & 1
        q_word |= (q_bit << i)

    while True:
        await RisingEdge(dut.clk)
        await settle()
        if int(dut.uo_out.value[1]) == 0:
            break

    return q_word


async def run_div_test(dut, x_real: float, y_real: float):
    x_word = float_to_fixed(x_real)
    y_word = float_to_fixed(y_real)

    dut._log.info(f"Test: {x_real} / {y_real}")
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
        f"Mismatch for {x_real}/{y_real}: "
        f"captured=0x{q_word:06X}, expected=0x{expected_word:06X}"
    )


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    clock = Clock(dut.clk, 20, unit="ns")  # 50 MHz
    cocotb.start_soon(clock.start())

    await reset_dut(dut)

    await run_div_test(dut, 1.5, 1.0)
    await ClockCycles(dut.clk, 5)
    await settle()

    await run_div_test(dut, 1.789634233478, 1.974231473301)
    await ClockCycles(dut.clk, 5)
    await settle()

    await run_div_test(dut, 1.25, 0.5)
    await ClockCycles(dut.clk, 5)
    await settle()

    dut._log.info("All tests passed")

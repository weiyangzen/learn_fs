# File Research: sources/os/plan9/plan9/sys/src/9/kw/uartkw.c

## Role

Kirkwood UART driver implementing Plan 9 `PhysUart`. It supports console registration, interrupt-driven input/output, baud/format configuration, and early serial output helpers.

This is console/serial hardware support, not filesystem code.

## Main Interfaces

- `kwphysuart`: physical UART operations table.
- `uartkirkwoodconsole`
- `serialputc`
- `serialputs`
- Internal operations:
  - `kw_pnp`
  - `kw_enable`
  - `kw_disable`
  - `kw_kick`
  - `kw_intr`
  - `kw_read`
  - `kw_getc`
  - `kw_putc`
  - `kw_baud`, `kw_bits`, `kw_stop`, `kw_parity`

## Data Structures

- `UartReg`: register layout for receiver/transmitter, interrupt enables, FIFO, line control, modem/status, scratch, and divisor registers.
- `Ctlr`: per-controller state with register pointer and enabled flag.
- Static `Uart` for the Kirkwood console.

## Important Behavior

- Uses `PHYSCONS` as the UART register base.
- Interrupt handler reads RX data and drains TX FIFO via Plan 9 UART helper callbacks.
- Baud changes program divisor latch registers.
- `serialputc` writes directly for early/last-resort output.

## Dependencies And Assumptions

- Depends on UART framework types and helpers.
- Uses interrupt `IRQ1uart0`.
- Assumes 16550-like register behavior.

## Notable Risks

- Early direct serial output bypasses normal locking.
- Hardware FIFO and modem control behavior is only minimally implemented.

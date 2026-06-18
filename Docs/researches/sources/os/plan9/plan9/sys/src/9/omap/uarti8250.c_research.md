# File Research: sources/os/plan9/plan9/sys/src/9/omap/uarti8250.c

OMAP35 8250-like UART driver for the console UART, integrated with Plan 9 `Uart`/`PhysUart`.

Key responsibilities:
- Defines 8250/OMAP UART registers and bit constants.
- Configures a single console UART at `PHYSCONS`, IRQ 74, exposed as `"COM3"`.
- Implements status, FIFO, DTR/RTS, modem control, parity, stop bits, data bits, baud, break, kick/transmit, interrupt handling, enable/disable, getc/putc, and console setup hooks.
- Provides early polled serial output before normal queues and interrupts are available.
- Connects `kbdq`, `serialoq`, and `consuart` in `i8250console`.
- Provides `_uartputs` and `_uartprint` early/debug output helpers.

Important behavior:
- Baud-rate programming is disabled under `#ifdef notdef`; requested baud is stored but hardware divisor is not changed.
- `i8250enable` refuses to do work when `up == nil`, preventing too-early interrupt setup.
- Early output path writes directly to `PHYSCONS` while holding high interrupt priority.
- Transmit interrupt is disabled when output queues drain and transmitter is empty.
- Receive interrupt consumes bytes unless break/framing/parity errors occurred.

Dependencies:
- Depends on Plan 9 generic UART layer, IRQ enable/disable, queue functions, and OMAP MMIO mapping.

Notable risks:
- Only one UART is declared, despite OMAP having multiple UARTs.
- FIFO enable changes flush hardware FIFOs, with comments noting possible receive data loss.
- Some PC 8250 workarounds/comments are retained even when not fully applicable to OMAP.

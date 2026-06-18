# File Research: sources/os/plan9/plan9/sys/src/9/mtx/uarti8250.c

Implements the MTX 8250/16550-compatible serial driver and early console binding.

Key points:
- Defines COM1/COM2 base ports, IRQs, UART register offsets, interrupt bits, FIFO bits, line-control bits, modem-control bits, line-status bits, and modem-status bits.
- Provides two `Ctlr` instances and two `Uart` instances chained as COM1 and COM2, using `PhysUart i8250physuart`.
- Maintains sticky register shadows for `Ier`, `Lcr`, and `Mcr` so writes can preserve persistent bits.
- Implements status reporting with baud, hangup flags, DSR/DCD/CTS/RI state, FIFO state, framing and overrun counters.
- Controls FIFO enable/reset, DTR, RTS, modem interrupts, parity, stop bits, word length, baud divisor, break signaling, and TX kicking.
- `i8250interrupt()` handles modem-status, THR-empty, receive-data, timeout, and line-error cases, feeding receive bytes to `uartrecv()` and output via `uartkick()`.
- `i8250enable()` optionally registers interrupts, enables RX/TX interrupts, and asserts DTR/RTS; `i8250disable()` shuts down line controls, interrupts, and FIFOs.
- Provides polled `getc`/`putc` for early console.
- `i8250console()` reads `console` from `getconf()`, configures `b9600 l8 pn s1`, enables without interrupts, and sets `consuart`.

Dependencies and interactions:
- Implements the physical UART backend consumed by generic UART/console layers.
- Uses `intrenable()` from `trap.c`.
- Boot code calls `i8250console()` before normal device setup.

Research relevance:
- Serial console and UART hardware support for MTX, including early polling mode and later interrupt-driven operation.

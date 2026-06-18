# File Research: sources/os/plan9/plan9/sys/src/9/pc/uarti8250.c

Purpose: Generic `PhysUart` driver named `i8250` for 8250-compatible serial ports, including COM1/COM2 and other wrappers that allocate i8250 controller state.

Main structures:
- `Ctlr`: I/O base, IRQ, PCI tag, interrupt-enabled flag, sticky register shadows, FIFO capability/status, and lock.
- Static `i8250ctlr[2]`/`i8250uart[2]`: built-in COM1 and COM2 definitions.

Key logic:
- Register constants define standard 8250/16450/16550-compatible UART registers and bits.
- `i8250enable` detects FIFO support, optionally registers the interrupt handler, enables received-data and THR-empty interrupts, sets modem IRQ-enable bit, asserts DTR/RTS, and clears pending interrupt events.
- `i8250disable` drops DTR/RTS, disables FIFO and interrupts, and unregisters IRQ if active.
- `i8250interrupt` loops until no pending interrupt, handling modem status changes, THR-empty transmit, and received data/line status/timeouts.
- `i8250kick` writes staged output while THR is empty, bounded to 128 bytes per call.
- `i8250fifo`, `i8250baud`, `i8250bits`, `i8250stop`, `i8250parity`, `i8250break`, `i8250modemctl`, `i8250rts`, `i8250dtr`, and `i8250status` implement `devuart` operations.
- `i8250getc`/`i8250putc` provide polled console I/O.
- `i8250alloc` lets ISA/PCI glue create additional i8250-compatible ports.
- `i8250config`, `i8250console`, `i8250mouse`, and `i8250setmouseputc` wire console and mouse serial uses.

Dependencies and integration:
- Implements Plan 9 `PhysUart i8250physuart`.
- Used directly for COM1/COM2 and indirectly by `uartisa.c` and `uartpci.c`.
- Depends on port I/O, interrupt registration, and `devuart` queue/staging helpers.

Risks and notes:
- FIFO changes can flush hardware FIFOs; code waits for transmitter empty but receive-side loss is still acknowledged as unavoidable.
- Uses sticky shadow registers because some UART registers are write-only or stateful.
- Console configuration is driven by the `console` config string.

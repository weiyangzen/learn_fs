# File Research: sources/os/plan9/9front/sys/src/9/teg2/uarti8250.c

Tegra console UART driver using an 8250-like register model.

Purpose:
- Provides `PhysUart i8250physuart` and sets `consuart` for early and normal console I/O.

Key behavior:
- Defines UART register offsets and bit masks for line control, FIFO, modem, interrupt, and line status.
- Implements status reporting, FIFO setup, DTR/RTS, modem control, parity/stop/bits configuration, break, interrupt-driven transmit/receive, enable/disable, and polled getc/putc.
- Uses sticky shadow registers for write-only or stateful registers.
- `uartconsinit` binds the single configured UART at `PHYSCONS`.

Integration:
- Used early by `main.c`/`l.s` boot diagnostics and later by Plan 9 UART/console layers.
- IRQ registration goes through `irqenable` from `trap.c`.

Risks/notes:
- Baud-rate programming is disabled under `notdef`; speed is effectively not changed.
- FIFO changes can lose receive data, so code waits for transmitter empty before toggling FIFO state.

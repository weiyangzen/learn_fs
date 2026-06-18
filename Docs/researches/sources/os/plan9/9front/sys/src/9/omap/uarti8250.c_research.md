# File Research: sources/os/plan9/9front/sys/src/9/omap/uarti8250.c

OMAP 8250-like UART driver, using OMAP UART3 as Plan 9 console COM3.

Key behavior:
- Defines standard 8250 register offsets and bits plus OMAP mode register handling.
- Registers one UART at `PHYSCONS`, IRQ 74, as the console.
- Maintains sticky write state for registers whose bits must be preserved.
- Implements Plan 9 `PhysUart` operations for enable/disable, FIFO, kick, break, baud, bits, stop, parity, modem control, DTR/RTS, status, getc, and putc.
- `i8250enable` sets UART mode, detects FIFO, optionally enables IRQ, and initializes DTR/RTS.
- `i8250interrupt` handles modem status, transmitter empty, receive-data, line-status, and timeout interrupts.
- `uartconsinit` selects this UART as `consuart` and configures `115200 8N1`.

Research notes:
- Baud-rate programming is disabled under `#ifdef notdef`; the configured baud is recorded but hardware speed is not changed there.
- Comments say UART0/UART1 exist but are not believed to be externally connected.

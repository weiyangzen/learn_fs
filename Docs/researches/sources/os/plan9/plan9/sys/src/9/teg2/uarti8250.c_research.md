# File Research: sources/os/plan9/plan9/sys/src/9/teg2/uarti8250.c

8250-like UART driver for the Tegra console.

Key behavior:
- Defines 8250 register offsets and bit masks.
- Provides one console UART at `PHYSCONS` with IRQ `Uartirq`.
- Supports status reporting, FIFO setup, modem control, parity/stop/bits, break, kick/output, interrupt receive/transmit, enable/disable, polling getc, and putc.
- Uses early brute-force polled output before normal console queues are ready.
- `i8250console` wires UART input/output queues into `kbdq`, `serialoq`, and `consuart`.

Important functions:
- `i8250enable`, `i8250interrupt`, `i8250kick`, `i8250putc`, `serialputc`, `_uartputs`, `i8250console`.

Notes:
- Baud-rate programming is disabled; the driver records requested baud but leaves hardware speed unchanged.
- OMAP-style `Mdr` mode register support remains in the common 8250-derived code.

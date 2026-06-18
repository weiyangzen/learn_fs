# File Research: sources/os/plan9/plan9/sys/src/9/rb/uarti8250.c

Single-console 8250-like UART driver for the RouterBoard port, using memory-mapped 32-bit CSR slots at `PHYSCONS`.

Key responsibilities:
- Defines one `Ctlr` and one console `Uart` named `cons`, wired to `ILduart0`.
- Implements the `PhysUart` interface: enable/disable, kick, break, baud/bits/stop/parity, modem control, RTS/DTR, FIFO, status, getc, and putc.
- Provides early output fallback when `normalprint` is false by polling raw `PHYSCONS` registers directly.
- Handles UART interrupts for modem status, transmit-empty, receive-ready, line-status, and character-timeout conditions.
- Stages output through Plan 9 UART queues and re-enables transmit-empty interrupts while data remains.
- Provides `i8250console()` to bind the UART queues to `kbdq`, `serialoq`, `consuart`, and console input conversion.
- Exposes `_uartputs`, `_uartprint`, `serialputc`, `serialputs`, and `serialkick` for low-level console users.

Important behavior:
- Baud-rate programming is disabled under `#ifdef notdef`; `i8250baud` records the requested baud but does not change hardware speed.
- `i8250enable` probes FIFO support once before enabling interrupts and clears pending events by calling the interrupt handler immediately.
- A periodic clock callback can poll the interrupt handler to recover stuck output.

Dependencies and assumptions:
- Depends on the generic `devuart.c` framework, `intrenable`, APB interrupt routing in `trap.c`, and Plan 9 queues.
- Assumes only the first UART is the console and uses `normalprint` to distinguish early boot from normal queue-backed output.

Notable risks:
- FIFO changes wait for transmitter empty and may drop receive-side data by design.
- Several comments note forced `Ethre` and polling workarounds whose underlying hardware cause is not fully known.

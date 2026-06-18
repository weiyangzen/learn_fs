# File Research: sources/teaching/xv6-riscv/kernel/uart.c

Implements the low-level 16550a UART driver.

Important behavior:
- Defines MMIO register accessors for UART registers.
- `uartinit()` configures baud rate, word length, FIFOs, interrupts, and transmit lock.
- `uartwrite()` writes bytes using transmit-complete interrupts and sleeps while busy.
- `uartputc_sync()` writes a byte synchronously for panic/print/echo paths.
- `uartintr()` acknowledges interrupts, wakes transmit waiters, and feeds received characters to `consoleintr()`.

Filesystem relevance: console device reads/writes depend on UART. Console is reachable through normal filesystem device-file paths.

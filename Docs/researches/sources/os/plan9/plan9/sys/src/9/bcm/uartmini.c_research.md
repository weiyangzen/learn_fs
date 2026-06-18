# File Research: sources/os/plan9/plan9/sys/src/9/bcm/uartmini.c

BCM2835 mini-UART and GPIO helper driver.

Key behavior:
- Defines GPIO and AUX mini-UART register offsets/bits.
- Provides GPIO helpers for function select, pull disable, output set/clear, and input read.
- Defines a `Uart` instance and `PhysUart miniphysuart`.
- `enable()` muxes GPIO 14/15 to Alt5, disables pulls, enables mini-UART, configures 8-bit mode, RX/TX, baud, and optional IRQs.
- Interrupt handler drains RX, feeds `uartrecv()`, and kicks TX when ready.
- `kick()` stages output and toggles TX interrupt enable.
- Supports baud, bits, stop, parity, RTS, status, blocking `getc()`/`putc()`, and console initialization from `console` config.
- `okay()` controls the OK LED via GPIO 16.

The driver names the UART `"uart0"` despite using BCM mini-UART/UART1 hardware.

# File Research: sources/os/plan9/plan9/sys/src/9/omap/devuart.c

Implements the generic Plan 9 UART `#t` device layer over physical UART backends.

Key points:
- Discovers `PhysUart` providers through `physuart[]`, builds a linked UART list, allocates `eiaN`, `eiaNctl`, and `eiaNstatus` directory entries.
- `uartenable()` opens/reopens input/output queues, initializes staging buffers, default serial settings, enables hardware, and links the UART into the enabled list.
- `uartdisable()` calls hardware disable and removes from enabled list.
- Supports special mouse UART use through `uartmouse()` and `uartsetmouseputc()`.
- Device methods implement attach/walk/stat/open/close/read/write/wstat/power for `#t`.
- `uartctl()` parses serial control commands: baud, bits, stop, parity, break, DTR/RTS, FIFO, modem control, hangup behavior, queue sizing, nonblocking, timer interval, and XON/XOFF.
- `uartwrite()` writes data to output queues or applies control commands.
- `uartclock()` periodically drains interrupt input staging, handles hangups, applies CTS/XON backoff, and kicks output.
- `uartstageoutput()`, `uartkick()`, `uartrecv()`, and `uartstageinput()` amortize queue operations and manage software/hardware flow control.
- Provides polling console helpers `uartgetc()`, `uartputc()`, and `uartputs()` using `consuart`, with fallback to `lprint`.

Dependencies and interactions:
- Physical UART implementations supply `PhysUart` methods.
- `devcons.c` uses `kbdq`, `serialoq`, and `consuart` set here.
- `clock.c` callback infrastructure drives periodic staging.

Research relevance:
- Portable UART device layer used by the OMAP serial console and serial ports.

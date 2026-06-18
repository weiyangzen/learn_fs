# File Research: sources/teaching/xv6-riscv/kernel/console.c

Implements console input and output over UART, including the console device entries in `devsw[CONSOLE]`.

Important behavior:
- `consputc()` writes characters synchronously through `uartputc_sync()` and handles backspace display.
- `consolewrite()` copies user/kernel source data in small chunks and sends it through `uartwrite()`.
- `consoleread()` blocks until a complete line, EOF, or full buffer is available, then copies to user/kernel destination.
- `consoleintr()` handles UART input characters, editing controls, EOF, process dump, echoing, and wakeups.
- `consoleinit()` initializes the console lock, UART, and device switch read/write handlers.

Filesystem relevance: console is exposed as a `T_DEVICE` inode via the file/device layer. It participates in normal `read`/`write` paths through `file.c` and `sysfile.c`.

# File Research: sources/teaching/xv6-public/console.c

Implements kernel console output, console input buffering, panic reporting, and console device registration.

Key behavior:
- `cprintf` supports `%d`, `%x`, `%p`, `%s`, and `%%` for kernel diagnostics.
- `panic` disables locking, prints CPU/panic/caller PCs, sets `panicked`, and spins.
- `cgaputc` writes to CGA text memory at `0xb8000`, manages cursor ports, backspace, newline, and scrolling.
- `consputc` mirrors output to UART and CGA.
- `consoleintr` handles input from keyboard/UART providers, including `^P` process dump, `^U` kill-line, backspace, `^D`, newline wakeups, and ring-buffer limits.
- `consoleread` and `consolewrite` implement device read/write operations with inode unlock/relock around blocking/printing.
- `consoleinit` registers `devsw[CONSOLE]` and enables keyboard IRQ routing.

Important interactions:
- Uses `sleep`/`wakeup` on `input.r`.
- Calls `procdump` after releasing console lock to avoid recursive lock trouble.

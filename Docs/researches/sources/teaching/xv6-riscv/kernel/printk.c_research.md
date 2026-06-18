# File Research: sources/teaching/xv6-riscv/kernel/printk.c

Implements kernel formatted printing and panic handling.

Important behavior:
- `printk()` supports a small set of format specifiers: integers, hex, pointers, chars, strings, and literal percent.
- A spinlock prevents interleaved output unless panic handling is active.
- `panic()` marks panic state, prints the panic message, marks the system panicked, and spins forever.
- `printkinit()` initializes the print lock.

Filesystem relevance: used throughout filesystem, log, block allocator, trap, and device code for diagnostics and fatal consistency checks.

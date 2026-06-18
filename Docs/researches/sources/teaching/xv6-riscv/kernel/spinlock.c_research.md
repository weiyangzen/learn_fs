# File Research: sources/teaching/xv6-riscv/kernel/spinlock.c

Implements low-level spinlocks and interrupt nesting discipline.

Important behavior:
- `initlock()` initializes lock state and debug name.
- `acquire()` disables interrupts with `push_off()`, checks recursive acquisition, and atomically swaps `locked`.
- `release()` verifies ownership, clears owner, atomically stores unlocked, and calls `pop_off()`.
- `holding()` checks current CPU ownership.
- `push_off()`/`pop_off()` provide nested interrupt disabling/restoration.

Filesystem relevance: protects short critical sections across the buffer cache, file table, inode table, log, pipes, console, UART, allocator, and process table. Correct interrupt discipline prevents deadlock with interrupt handlers.

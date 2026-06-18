# File Research: sources/teaching/xv6-riscv/kernel/syscall.c

Implements syscall argument fetching and syscall dispatch.

Important behavior:
- `fetchaddr()` copies a 64-bit user value with bounds checks.
- `fetchstr()` copies a NUL-terminated user string.
- `argraw()`, `argint()`, `argaddr()`, and `argstr()` retrieve syscall arguments from trapframe registers.
- `syscalls[]` maps syscall numbers to handler functions.
- `syscall()` dispatches by `a7` and stores return value in `a0`.

Filesystem relevance: all filesystem syscalls enter through this dispatcher. Path strings, user buffers, file descriptors, and mode flags are fetched here or by helpers built on this API.

# File Research: sources/os/plan9/9front/sys/src/9/port/ucalloc.c

Uncached-memory allocator built on a Plan 9 `Pool`.

Key responsibilities:
- Defines a dedicated `Uncached` pool with 4 MiB max size, 1 MiB arenas, 32-byte quantum, and custom lock/print/panic hooks.
- Allocates new 1 MiB arenas from normal memory and maps them uncached with `mmuuncache()`.
- Temporarily increases `mainmem->maxsize` while provisioning uncached arena memory.
- Provides `ucalloc()`, `ucallocalign()`, and `ucfree()` wrappers.
- Zeroes allocated buffers before returning them.

Dependencies:
- Uses kernel `Pool` allocator, `mallocalign`, `mmuuncache`, and interrupt-lock-backed private logging.

Notable behavior:
- `ucarena()` asserts arena size is exactly 1 MiB.
- `ucallocalign()` asserts individual allocations are smaller than `minarena - 128`.
- Pool diagnostic output is buffered under an interrupt lock and printed on unlock.

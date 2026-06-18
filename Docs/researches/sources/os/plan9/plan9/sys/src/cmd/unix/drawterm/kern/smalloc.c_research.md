# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/smalloc.c

This file provides minimal allocation wrappers for drawterm kernel code.

Key behavior:
- `smalloc` calls `malloc`, zeroes the returned memory, and raises `Enomem` on failure.
- `malloc` wraps `calloc(n, 1)`.

Important details:
- Both paths zero memory, so `smalloc` redundantly clears allocations from this local `malloc`.
- This hosted kernel uses fatal/error-style allocation behavior rather than propagating `NULL` in many call sites.

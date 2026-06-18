# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ialloc.c

This file defines one allocation helper.

Behavior:
- `ialloc(ulong n)` calls `malloc(n)` and zeroes the allocation with `memset` if successful.
- Returns `nil`/`0` on allocation failure.

Role:
- Used throughout KFS startup and device initialization for zero-initialized global/runtime allocations.

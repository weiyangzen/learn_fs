# File Research: sources/teaching/xv6-public/spinlock.c

Implements xv6 spinlocks and interrupt-disable nesting.

Key behavior:
- `initlock` initializes debug fields and unlocked state.
- `acquire` disables interrupts with `pushcli`, detects recursive acquisition, atomically spins on `xchg`, issues a memory barrier, and records owner/caller PCs.
- `release` validates ownership, clears debug fields, issues memory barrier, atomically clears lock, and calls `popcli`.
- `getcallerpcs` walks frame pointers for debugging.
- `holding` checks whether current CPU owns a lock.
- `pushcli`/`popcli` maintain per-CPU interrupt-disable nesting and restore interrupts only when nesting returns to zero.

Important interactions:
- Requires valid `mycpu()` state, so interrupt state and CPU initialization order matter.

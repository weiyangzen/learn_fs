# File Research: sources/teaching/xv6-riscv/kernel/spinlock.h

Defines `struct spinlock`.

Fields:
- `locked` stores lock state.
- `name` is debug metadata.
- `cpu` records the owning CPU for `holding()` and diagnostics.

Filesystem relevance: spinlocks appear in all core shared filesystem-adjacent tables and queues: buffer cache, inode table, log state, file table, pipe state, console, and virtio disk.

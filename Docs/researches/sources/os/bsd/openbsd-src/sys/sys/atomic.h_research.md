# File Research: sources/os/bsd/openbsd-src/sys/sys/atomic.h

Purpose: Provides generic atomic operations and memory-barrier macros with machine override hooks.

Key behavior:
- Includes machine atomic definitions first, then supplies fallback inline implementations when an architecture has not defined a primitive.
- Provides compare-and-swap for unsigned int, unsigned long, and pointers.
- Provides atomic swap for unsigned int, unsigned long, and pointers.
- Provides add/subtract with return-new-value variants and void-return wrappers.
- Defines increment/decrement operations in terms of add/subtract.
- In kernel builds, defines simple volatile load/store helpers.
- Defines memory barriers (`membar_enter`, `membar_exit`, producer, consumer, sync, and atomic-adjacent barriers) using `__sync_synchronize()` fallbacks.
- Defines kernel `READ_ONCE()` and `WRITE_ONCE()` helpers plus Alpha data-dependency consumer barrier handling.

Filesystem relevance:
- VFS, vnode, buffer, lock, and device paths rely on these primitives for reference counts, state flags, lock internals, and cross-CPU visibility.

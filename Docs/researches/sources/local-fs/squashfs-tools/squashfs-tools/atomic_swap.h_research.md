# File Research: sources/local-fs/squashfs-tools/squashfs-tools/atomic_swap.h

Provides `atomic_swap()` for `struct read_entry **`.

Two implementations:
- Default: uses GCC/Clang `__atomic_exchange_n(entry, NULL, __ATOMIC_SEQ_CST)`.
- Fallback under `DONT_USE_ATOMIC_EXCHANGE_N`: locks a supplied `pthread_mutex_t`, reads `*entry`, clears it to `NULL`, and unlocks.

Key role: lockless or mutex-backed handoff primitive for reader synchronization.

Notable detail: the fallback uses pthread cleanup handlers so cancellation unlocks the mutex correctly.

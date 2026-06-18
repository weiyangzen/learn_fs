# File Research: sources/os/bsd/freebsd-src/sys/sys/_blockcount.h

Minimal block count type and reader.

Defines:
- `blockcount_t` with a single unsigned integer field.
- High-bit waiter flag `_BLOCKCOUNT_WAITERS_FLAG`.
- `_BLOCKCOUNT_COUNT()` and `_BLOCKCOUNT_WAITERS()` helpers.
- `blockcount_read()` using `atomic_load_int()` and masking off the waiter flag.

Research relevance:
- Compact atomic counter representation where count and waiter state share one word.

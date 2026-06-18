# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rwlock_impl.h

## Role

`rwlock_impl.h` defines implementation-private layout and bit encodings for kernel readers-writer locks.

## Layout and Bits

`rwlock_impl_t` stores a single `uintptr_t rw_wwwh`, packing waiters, writer-wanted state, write-locked owner, and reader hold count.

Bit meanings:
- `RW_HAS_WAITERS`
- `RW_WRITE_WANTED`
- `RW_WRITE_LOCKED`
- `RW_READ_LOCK`

`RW_WRITE_LOCK(thread)` encodes writer ownership by OR-ing the thread pointer with the write-locked bit. Hold-count and owner masks are derived from `-RW_READ_LOCK`.

## Query Macros

The `_RW_READ_HELD`, `_RW_WRITE_HELD`, `_RW_LOCK_HELD`, and `_RW_ISWRITER` macros are used both by rwlock implementation code and DTrace subroutines, which cannot call the normal `rw_*()` functions.

## Research Notes

This is a low-level synchronization representation header. Pointer alignment, bit packing, and current-thread writer ownership assumptions are essential; changes here affect rwlock internals and DTrace lock-state inspection.

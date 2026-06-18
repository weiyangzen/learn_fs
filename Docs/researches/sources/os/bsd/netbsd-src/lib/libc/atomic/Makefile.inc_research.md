# File Research: sources/os/bsd/netbsd-src/lib/libc/atomic/Makefile.inc

## Summary
Build and manual-page fragment for libc atomic operations.

## Key Details
- Adds `${.CURDIR}/atomic` to `.PATH`.
- Registers manuals for atomic add, and, compare-and-swap, decrement, increment, or, swap, generic atomic ops, and memory barriers.
- Defines extensive `MLINKS` for width-specific, type-specific, no-interlock, and new-value-returning atomic APIs.
- Adds aliases such as `atomic.3` to `atomic_ops.3` and `membar.3` to `membar_ops.3`.

## Notes
This fragment is documentation-oriented; it does not list implementation sources in the shown file.

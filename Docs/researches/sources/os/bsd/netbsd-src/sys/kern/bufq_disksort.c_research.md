# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_disksort.c

## Purpose
Implements the traditional disk seek-sort buffer queue strategy as a loadable `MODULE_CLASS_BUFQ` module.

## Main Interfaces
- `BUFQ_DEFINE(disksort, 20, bufq_disksort_init)` registers strategy metadata.
- `bufq_disksort_put()` inserts buffers into a two-list ascending scan order using `buf_inorder()`.
- `bufq_disksort_get()` returns/removes the head request.
- `bufq_disksort_cancel()` removes a specific queued buffer.
- `bufq_disksort_init()`/`fini()` allocate and free private queue state.
- Module command registers/unregisters `bufq_strat_disksort`.

## Implementation Notes
The queue models a one-way scan: requests after the active position form the first sorted list, while requests already passed form the second sorted list.

## Dependencies
Uses `TAILQ`, `struct buf`, bufq framework hooks, kmem allocation, and module infrastructure.

# File Research: sources/os/bsd/freebsd-src/sys/sys/queue_mergesort.h

Read completely: 217 lines.

## Purpose
Adds merge and mergesort macros for the queue types defined in `sys/queue.h`.

## Main Elements
- Provides shims to normalize differing queue macro signatures across SLIST, LIST, STAILQ, and TAILQ.
- Defines `SYSQUEUE_MERGE()` to pull entries from one sorted list into another using a `qsort_r`-style comparator.
- Defines `SYSQUEUE_MERGE_SUBL()` to merge sorted sublists inside a working list.
- Defines `SYSQUEUE_MERGESORT()` using bottom-up power-of-two sorted-run invariants, moving all elements into a working list and then concatenating sorted output back.
- Exposes `SLIST_MERGESORT`, `LIST_MERGESORT`, `STAILQ_MERGESORT`, `TAILQ_MERGESORT`, and corresponding `*_MERGE` macros.

## Dependencies And Integration
Depends on queue head/entry operations from `sys/queue.h` and caller-provided comparator signature `cmp(a, b, thunk)`.

## Risk Notes
The macros mutate list heads and element links in place. Comparator consistency and correct queue type/field arguments are required; macro expansion can be large and has no type-safe wrapper.

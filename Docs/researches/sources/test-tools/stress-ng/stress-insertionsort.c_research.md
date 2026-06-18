# sources/test-tools/stress-ng/stress-insertionsort.c

## Purpose
`stress-insertionsort.c` stresses CPU, cache, and memory with a simple insertion sort over 32-bit integer arrays, using forward and reverse order passes to drive worst-case data movement and comparison work.

## Important APIs, Types, And Functions
Option `insertionsort-size` controls element count. `insertionsort_fwd()` sorts ascending and returns a comparison/move count approximation. `insertionsort_rev()` sorts descending. `stress_insertionsort()` allocates data with `stress_mmap_populate()`, names/collapses the mapping, installs an optional `SIGALRM` longjmp handler, initializes data through `core-sort`, repeatedly shuffles/sorts/verifies/mangles, and records comparison metrics.

## Control Flow
The stressor chooses size from settings or min/max flags, mmaps the data, initializes sort data, waits at the barrier, then loops: shuffle, ascending insertion sort, optional ascending verification, descending sort, optional descending verification, mangle data, descending sort again, optional verification, and bogo increment. Signal longjmp exits to cleanup if configured.

## State And Persistence
All state is memory-only: the anonymous data mapping, local duration/count totals, and optional signal-jump globals. It writes no files.

## Dependencies And Integration Points
It uses stress-ng mmap/madvise/signal/sort helpers, target-clone optimization, metrics, process state, and verify/minimize/maximize flags.

## Risks
Insertion sort is O(n^2); max size can run for a long time and heavily stress memory bandwidth. The reverse comparison counter expression can undercount in some cases but is used only for metrics. Signal longjmp must restore handlers and unmap memory. Verification is optional and linear.

## Test Signals
Signals include verify-mode ordering checks, clean SIGALRM exit, min/max size behavior, no mmap leak, bogo progress, and populated comparisons/sec and comparisons/item metrics.

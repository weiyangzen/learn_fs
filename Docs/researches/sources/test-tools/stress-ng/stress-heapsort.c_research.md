# sources/test-tools/stress-ng/stress-heapsort.c

## Purpose
`stress-heapsort.c` stresses CPU, cache, and memory by repeatedly heap-sorting arrays of 32-bit integers using either libc/BSD `heapsort()` when available or a local non-libc heapsort implementation.

## Important APIs, Types, And Functions
Options are `heapsort-size`, `heapsort-method`, and `heapsort-ops`. `heapsort_nonlibc()` implements heap construction and extraction using stress-ng sort copy/swap helpers. `stress_heapsort_methods[]` maps `heapsort-libc` and `heapsort-nonlibc` to function pointers. `stress_heapsort()` allocates data with `stress_mmap_populate()`, initializes and shuffles data through `core-sort`, sorts forward and reverse, verifies ordering when requested, and records comparison metrics.

## Control Flow
The stressor selects a method and array size, mmaps anonymous data, optionally installs a `SIGALRM` longjmp handler, initializes sorted data, waits at the sync barrier, then loops: shuffle, forward sort, optional ascending verification, reverse sort, optional descending verification, mangle data, reverse sort again, optional verification, and bogo increment. On alarm longjmp or stop it restores signal handling, sets deinit state, records metrics, and unmaps memory.

## State And Persistence
State is memory-only: the data mapping, comparison counters maintained by `core-sort`, local duration/count totals, and optional static signal-jump globals. It writes no files.

## Dependencies And Integration Points
It depends on stress-ng mmap/madvise/signal/sort helpers, optional libc/BSD heapsort availability, `HAVE_SIGLONGJMP`, and global verify/minimize/maximize flags.

## Risks
The non-libc implementation uses variable-length stack temporary storage sized by element size; current callers use 32-bit integers, keeping that safe. `siglongjmp` can bypass loop internals and requires careful restoration. Large sizes can create long O(n log n) runs and memory pressure. Libc heapsort semantics may differ by platform.

## Test Signals
Run both method choices when available, verify ascending/descending order under `--verify`, exercise min/max sizes, confirm `SIGALRM` exits cleanly, and check comparison-per-second and comparison-per-item metrics.

# sources/test-tools/fio/engines/mmap.c

## Purpose
Implements fio's memory-mapped file engine. It maps a whole file when feasible or maps per-I/O windows when necessary, performs read/write as memory copies, and implements sync by `msync()`.

## Important APIs, Types, And Functions
`struct fio_mmap_data` stores mapped pointer, mapped size, and map offset per file. When transparent hugepage support is compiled, `struct mmap_options` exposes `thp`. Key functions are `fio_mmapio_init()`, `fio_mmap_file()`, `fio_mmapio_prep_full()`, `fio_mmapio_prep_limited()`, `fio_mmapio_prep()`, `fio_mmapio_queue()`, `fio_mmapio_open_file()`, and `fio_mmapio_close_file()`.

## Control Flow
`init` rejects sub-page minimum block sizes when direct/sync options require page granularity and divides a 1 GiB mapping cap across files for 32-bit safety. File open uses generic open and attaches per-file mapping state. `prep` reuses an existing mapping if the requested offset/length fits; otherwise it unmaps, attempts a full-file map, and falls back to a limited window if the full map fails or is too large. Mapping protection is derived from workload direction and verify settings. `queue` copies from/to the mapped region, calls `msync()` for sync, delegates trim to fio, and for `direct=1` forces `msync()` plus `POSIX_MADV_DONTNEED` on the touched range.

## State And Persistence
Per-file mapping state is stored in `FILE_ENG_DATA`. The file's partial-mmap flag records that full mapping is unsuitable. Writes persist to the mapped file according to normal mmap and `msync` semantics.

## Dependencies And Integration Points
Depends on POSIX `mmap`, `munmap`, `msync`, `posix_madvise`, optional `MADV_HUGEPAGE`, fio generic file helpers, and fio verify/read/write settings.

## Risks
`fio_mmapio_close_file()` frees mapping metadata but does not unmap an active mapping, so correctness depends on prior prep/unmap behavior or process cleanup. Full-map fallback clears fio error before limited mapping. `MAP_PRIVATE` is used when `thp` is requested, changing write persistence semantics. Direct I/O behavior is simulated with sync/drop-cache advice rather than true O_DIRECT.

## Test Signals
Test full-file and partial-window mapping, 32-bit/large-file fallback, read/write/verify protections, sync and trim, `direct=1` drop behavior, THP option behavior, fadvise/madvise combinations, unaligned page-size rejection, and repeated offsets that reuse vs remap.

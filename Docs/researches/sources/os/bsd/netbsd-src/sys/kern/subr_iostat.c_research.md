# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_iostat.c

Read completely: 506 lines.

Implements kernel I/O statistics objects and legacy-compatible `hw.disk*`/`hw.iostat*` sysctls. A global `iostatlist` tracks all `struct io_stats` records under `iostatlist_lock`.

Core behavior:
- `iostat_alloc()`, `iostat_free()`, `iostat_rename()`, and `iostat_find()` manage stats object lifetime and names.
- `iostat_wait()`, `iostat_busy()`, and `iostat_unbusy()` maintain wait/busy counters, timestamps, cumulative time, and weighted time sums.
- `iostat_unbusy()` also accounts read/write byte and transfer counts.
- `iostat_seek()` increments seek counts.
- Sysctls return disk-only names, all iostat names, and arrays of `io_sysctl` records, including old `hw.diskstats` size behavior.

Risks and notes:
- Per-device counters are updated without an internal per-object lock; callers are expected to serialize appropriately.
- Time accumulation depends on balanced wait/busy/unbusy transitions.
- Name sysctl output is a space-separated string with NUL-copy behavior inherited from older interfaces.

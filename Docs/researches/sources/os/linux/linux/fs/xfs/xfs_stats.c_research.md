# File Research: sources/os/linux/linux/fs/xfs/xfs_stats.c

## Purpose

`xfs_stats.c` implements global and per-mount XFS statistics formatting, clearing, and legacy procfs compatibility endpoints. It is the implementation behind `/sys/fs/xfs/stats/stats`, per-mount stats sysfs files, and the older `/proc/fs/xfs/*` quota/stat paths when procfs is enabled.

## Main Interfaces

- `struct xstats xfsstats`: global XFS statistics object, with its per-CPU counter storage allocated during module init in `xfs_super.c`.
- `xfs_stats_format(struct xfsstats __percpu *stats, char *buf)`: emits the text statistics format expected by sysfs/procfs readers.
- `xfs_stats_clearall(struct xfsstats __percpu *stats)`: clears per-CPU statistics while preserving stateful inode counters.
- `xfs_init_procfs()` / `xfs_cleanup_procfs()`: create and remove `/proc/fs/xfs` compatibility entries under `CONFIG_PROC_FS`.
- `xqm_proc_show()` and `xqmstat_proc_show()`: legacy quota stat show callbacks under `CONFIG_XFS_QUOTA`.

## Implementation Notes

- `counter_val` sums a 32-bit counter index across all possible CPUs by treating each per-CPU `struct xfsstats` as a `uint32_t` array.
- `xfs_stats_format` uses a static table of stat group names and endpoint offsets. It prints grouped counters in the historic order: extent allocation, allocation btrees, block map, directories, transactions, inode grabs, log, AIL pushes, I/O, attributes, inode clustering, vnode-era counters, buffer cache, newer btree families, quota, zoned GC, and metafile counters.
- High precision counters are summed separately as 64-bit values: `xs_xstrat_bytes`, `xs_write_bytes`, `xs_read_bytes`, `xs_defer_relog`, and `xs_gc_bytes`.
- The `debug` line reports whether the kernel was built with `DEBUG`.
- `xfs_stats_clearall` preserves `xs_inodes_active` and `xs_inodes_meta`, because they represent current state rather than monotonic event counts.
- Procfs initialization creates `/proc/fs/xfs/stat` as a symlink to `/sys/fs/xfs/stats/stats`, then conditionally creates quota compatibility files.

## Dependencies and Callers

- Consumes layout definitions and macros from `xfs_stats.h`.
- Called by `xfs_sysfs.c` for sysfs stats reads and clears.
- Called by `xfs_sysctl.c` when the `stats_clear` sysctl is written.
- Global stats allocation, sysfs registration, and cleanup are orchestrated by `init_xfs_fs` and `exit_xfs_fs` in `xfs_super.c`.

## Research Notes

- The stats ABI is layout sensitive: group boundaries depend on field ordering in `struct __xfsstats`.
- Buffer length is bounded with `PATH_MAX - len`; callers must provide a buffer large enough for sysfs/procfs style output.
- Clearing is per-CPU and uses `preempt_disable` around each per-CPU update, but does not globally synchronize readers; readers can observe in-progress clears.

# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_stats.c

Implements XFS statistics aggregation, formatting, clearing, and legacy procfs compatibility.

Key elements:
- `struct xstats xfsstats` is the global statistics holder.
- `counter_val` sums a 32-bit statistic slot across all possible CPUs.
- `xfs_stats_format` emits grouped statistics text for sysfs/proc consumers. It groups counters by fixed endpoints that mirror `struct __xfsstats` layout, then separately sums higher-precision 64-bit counters such as `xs_xstrat_bytes`, `xs_write_bytes`, `xs_read_bytes`, `xs_defer_relog`, and `xs_gc_bytes`.
- `xfs_stats_clearall` zeros per-CPU stats but preserves stateful inode counters `xs_inodes_active` and `xs_inodes_meta`.

Procfs behavior under `CONFIG_PROC_FS`:
- Creates `/proc/fs/xfs`.
- Adds `/proc/fs/xfs/stat` as a symlink to `/sys/fs/xfs/stats/stats`.
- Under `CONFIG_XFS_QUOTA`, exposes legacy `xqmstat` and `xqm` proc entries backed by global quota counters.
- `xfs_cleanup_procfs` removes the entire proc subtree.

Important dependencies:
- Counter layout and offsets come from `xfs_stats.h`.
- Sysfs stats display in `xfs_sysfs.c` calls `xfs_stats_format`.
- Sysctl stats clearing in `xfs_sysctl.c` calls `xfs_stats_clearall`.

Research notes:
- Formatting relies on the exact order of fields in `struct __xfsstats`; adding counters requires updating both the struct and grouping table.
- The buffer limit uses `PATH_MAX`, so callers must provide a buffer large enough for the generated stats text.

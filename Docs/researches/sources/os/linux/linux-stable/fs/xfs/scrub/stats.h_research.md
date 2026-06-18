# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/stats.h

Declares the scrub statistics interface.

Key elements:
- `struct xchk_stats_run` carries per-run scrub time, repair time, retry count, and repair attempted/succeeded booleans.
- When `CONFIG_XFS_ONLINE_SCRUB_STATS` is enabled, declares global setup/teardown, mount allocation/free, debugfs register/unregister, and stats merge functions.
- `xchk_stats_now` returns `ktime_get_ns`.
- `xchk_stats_elapsed_ns` guarantees at least one nanosecond for clocks that return the same timestamp twice.

Disabled configuration:
- All public stats hooks compile to no-ops or zero values when stats are disabled.

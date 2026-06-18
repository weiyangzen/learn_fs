# File Research: sources/os/linux/linux/fs/xfs/scrub/stats.h

This header declares the online scrub statistics API and provides compile-time stubs when `CONFIG_XFS_ONLINE_SCRUB_STATS` is disabled.

Key type:
- `struct xchk_stats_run`: per-operation timing and retry/repair result data accumulated by `scrub.c`.

When stats are enabled, it declares:
- Global lifecycle: `xchk_global_stats_setup`, `xchk_global_stats_teardown`.
- Per-mount lifecycle: `xchk_mount_stats_alloc`, `xchk_mount_stats_free`.
- Debugfs registration: `xchk_stats_register`, `xchk_stats_unregister`.
- Merge function: `xchk_stats_merge`.
- Time helpers: `xchk_stats_now`, `xchk_stats_elapsed_ns`.

Time behavior:
- `xchk_stats_now()` returns `ktime_get_ns()`.
- `xchk_stats_elapsed_ns()` returns at least 1 ns if the clock did not advance, avoiding zero-duration runtime reports.

When stats are disabled:
- Lifecycle/register/merge operations compile to no-ops or success.
- Timing helpers compile to zero-returning expressions.

Risk notes:
- Callers can unconditionally call the stats API because disabled builds erase the overhead.
- The elapsed helper intentionally prevents “instantaneous” nonzero operations from disappearing from stats when clock resolution is coarse.

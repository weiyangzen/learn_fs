# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/stats.c

Implements optional online scrub statistics collection and debugfs reporting.

Key behavior:
- Tracks per-scrub-type counters for invocations, clean/corrupt/preen/cross-reference outcomes, incomplete/warning results, retries, repair attempts/successes, and scrub/repair runtime in microseconds.
- Maintains both global stats and per-mount stats.
- `xchk_stats_merge` updates global and mount stats after scrub runs.
- `xchk_stats_format` renders a text table with one row per named scrub type.
- `xchk_stats_estimate_bufsize` computes a worst-case snapshot buffer size.
- `xchk_stats_clearall` resets counters under each per-type spinlock.
- Debugfs exposes `scrub/stats` read-only and `scrub/clear_stats` write-only; writing `1` clears counters.
- Provides setup/teardown for global stats and allocation/free for per-mount stats.

Important details:
- `XFS_SCRUB_OFLAG_UNCLEAN` groups all output flags that prevent a run from counting as clean.
- Runtime accounting converts nanoseconds to microseconds with `howmany_64`.
- Counter state is protected per scrub type by `css_lock`.

# File Research: sources/os/linux/linux/fs/xfs/scrub/stats.c

This file implements optional online scrub statistics collection and debugfs reporting under `CONFIG_XFS_ONLINE_SCRUB_STATS`. It tracks per-scrub-type invocation outcomes, retry counts, repair attempts/successes, and cumulative runtime.

Key structures:
- `struct xchk_scrub_stats`: per-scrub-type counters and runtime totals protected by `css_lock`.
- `struct xchk_stats`: debugfs root plus an array indexed by `XFS_SCRUB_TYPE_NR`.
- `global_stats`: global aggregate stats object.
- `name_map[]`: maps scrub type numbers to debugfs text names.

Important entry points:
- `xchk_stats_merge`: merges one completed scrub run into global and per-mount stats.
- `xchk_global_stats_setup` / `xchk_global_stats_teardown`: initialize and expose global stats.
- `xchk_mount_stats_alloc` / `xchk_mount_stats_free`: allocate/free per-mount stats.
- `xchk_stats_register` / `xchk_stats_unregister`: create/remove debugfs files.
- `xchk_scrub_stats_read`: emits formatted stats snapshot.
- `xchk_clear_scrub_stats_write`: accepts `1` to clear counters.

Debugfs interface:
- Directory: `scrub`
- File `stats` is read-only and reports lines of:
  `name invocations clean corrupt preen xfail xcorrupt incomplete warning retries checktime_us repair_invocations repair_success repairtime_us`
- File `clear_stats` is write-only and clears all counters when userspace writes `1`.

Runtime accounting:
- Outcome counters are derived from scrub output flags.
- Clean means no corrupt/preen/xfail/xcorrupt/incomplete/warning output flag.
- Runtime nanoseconds from `xchk_stats_run` are rounded up into microseconds with `howmany_64`.
- Repair counters are based on `repair_attempted` and `repair_succeeded`.

Risk notes:
- Snapshot formatting is intentionally single-read: if file position is nonzero, read returns 0 to avoid fragmented/garbled text.
- Stats update uses per-type spinlocks, but formatting reads without taking those locks, so output is a best-effort live snapshot rather than a serialized transaction.
- `xchk_stats_teardown` currently has no dynamic work besides the surrounding debugfs/free paths.

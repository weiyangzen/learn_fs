# File Research: sources/os/linux/linux-stable/fs/netfs/stats.c

Defines and renders netfs support statistics.

Key behavior:
- Tracks read origins, read/cache/download outcomes, write origins, upload/cache-write outcomes, retry counts, active objects, folio queues, and writeback lock behavior.
- `netfs_stats_show()` prints netfs counters and then appends FS-Cache stats through `fscache_stats_show()`.
- Exported so proc setup and other code can render stats.

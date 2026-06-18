# File Research: sources/os/linux/linux/fs/netfs/stats.c

Defines generic netfs statistics counters and seq-file rendering.

Counters cover:
- Read entry points and subrequest/request object counts.
- Downloads, cache reads, zeroing, short reads, read retries.
- Buffered/write-through/direct/writeback/copy-to-cache write paths.
- Upload/cache-write completions and failures.
- Write retries.
- Writeback lock skip/wait counts.
- Folio queue allocations.

Important API:
- `netfs_stats_show()`: prints netfs counters and then calls `fscache_stats_show()`.

Export:
- `netfs_stats_show` is exported for proc integration.

Relationship:
- Displayed from `fs/netfs/stats` when enabled by config.

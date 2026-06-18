# File Research: sources/os/linux/linux/fs/netfs/fscache_stats.c

Defines FS-Cache statistics counters and procfs rendering.

Counters cover:
- Volumes, collisions, allocation failures.
- Cookies and LRU activity.
- Acquires, invalidates, updates, relinquishes, resizes.
- Cache I/O counts and no-space/cull events.

Important exported counters:
- `fscache_n_updates`.
- `fscache_n_read`.
- `fscache_n_write`.
- `fscache_n_no_write_space`.
- `fscache_n_no_create_space`.
- `fscache_n_culled`.
- `fscache_n_dio_misfit`.

Important API:
- `fscache_stats_show()`: appends FS-Cache statistics to the netfs stats seq file.

Notable behavior:
- Includes LRU timer pending delta in the `LRU` statistics line.

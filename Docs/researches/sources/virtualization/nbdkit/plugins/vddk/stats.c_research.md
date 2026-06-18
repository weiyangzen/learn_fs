# File Research: sources/virtualization/nbdkit/plugins/vddk/stats.c

Implements optional per-VDDK-API timing and byte statistics for debug flag `-D vddk.stats=1`.

Key behavior:
- Exports debug flag `vddk_debug_stats`.
- Defines global `stats_<VixDiskLib_fn>` structures for every API listed in `vddk-stubs.h` by macro expansion.
- Uses `stats_lock` to protect updates performed by inline `update_stats` in `vddk.h`.
- `display_stats` collects all stats into a vector, sorts by descending total microseconds, and logs function name, total time, call count, and bytes when nonzero.
- Strips `VixDiskLib_` prefix for display.

Dependencies:
- `vddk-stubs.h` macro list.
- nbdkit debug logging.
- vector utility.

Notes:
- Stats are emitted during plugin unload after `VixDiskLib_Exit`/`dlclose` handling in `vddk.c`.
- Datapath byte counts are supplied by callers, especially async read/write completion.

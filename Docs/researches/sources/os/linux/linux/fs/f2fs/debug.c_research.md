# File Research: sources/os/linux/linux/fs/f2fs/debug.c

## Summary
Implements F2FS debug/statistics collection and the debugfs `f2fs/status` report. It tracks per-mounted-filesystem state, segment distribution, cache sizes, dirty/writeback counters, checkpoint/GC metrics, extent-cache hit rates, and memory footprint estimates.

## Main Responsibilities
- Maintains the global `f2fs_stat_list`.
- Builds and destroys per-superblock `f2fs_stat_info`.
- Computes segment validity distribution and bimodal distribution factor.
- Aggregates multi-device segment/section usage.
- Reports dirty pages, inode counts, cache counters, checkpoint counters, GC activity, discard/flush state, and memory estimates.
- Creates/removes the debugfs root and `status` file when `CONFIG_DEBUG_FS` is enabled.

## Key APIs
- `f2fs_update_sit_info()`.
- `f2fs_build_stats()`.
- `f2fs_destroy_stats()`.
- `f2fs_create_root_stats()`.
- `f2fs_destroy_root_stats()`.

## Important Behavior
`update_general_status()` refreshes most live counters from `sbi`, NAT/SIT managers, dirty-page counters, extent-cache statistics, discard and flush controllers, checkpoint merge state, curseg positions, GC counters, and multi-device data.

`stat_show()` locks the global stats list, iterates all mounted F2FS instances, updates each status snapshot, and emits a large human-readable status report through `seq_file`.

`update_mem_info()` estimates static metadata memory, cache memory, extent-tree memory, and page-cache memory for node/meta/compression inode mappings.

## State and Synchronization
The global stats list is protected by `f2fs_stat_lock`. Checkpoint timing fields use `sbi->cprc_info.stat_lock`. Debugfs output reads many live counters atomically or through helper APIs, but it is primarily diagnostic and snapshot-oriented.

## Risks
The debug report combines values from many subsystems without taking all subsystem locks, so it should be treated as approximate live telemetry. Memory footprint estimates are manually maintained and can drift as F2FS structures evolve. Multi-device stats depend on segment-to-device boundary calculations staying consistent with resize and device layout state.

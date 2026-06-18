# File Research: sources/os/linux/linux-stable/fs/f2fs/sysfs.c

## Purpose
`sysfs.c` implements F2FS runtime observability and tuning through `/sys/fs/f2fs` and `/proc/fs/f2fs`.

## Main Responsibilities
- Creates the global `/sys/fs/f2fs` kset plus `features` and `tuning` kobjects.
- Creates per-mounted-filesystem kobjects for the mount, `stat`, and `feature_list`.
- Exposes many per-filesystem tunables and counters through generated `f2fs_attr` objects.
- Registers procfs diagnostic files under `/proc/fs/f2fs/<device>`.
- Cleans up all kobjects and procfs entries on unmount and module exit.

## Key Data and Interfaces
- `struct f2fs_attr` represents per-superblock sysfs entries, with target struct type, offset, size, show/store callbacks, and optional feature id.
- `struct f2fs_base_attr` represents global feature/tuning entries.
- `__struct_ptr` maps an attribute’s target enum to `f2fs_sb_info`, GC thread, segment manager, discard controller, node manager, stat info, checkpoint request controller, ATGC state, or fault injection state.
- Exported lifecycle functions:
  - `f2fs_init_sysfs`
  - `f2fs_exit_sysfs`
  - `f2fs_register_sysfs`
  - `f2fs_unregister_sysfs`

## Sysfs Coverage
The file exposes:
- Segment and space counters: dirty/free/overprovisioned segments, unusable blocks, reserved blocks, lifetime written KB.
- GC controls: urgent/idle modes, sleep times, migration granularity, victim search, pin thresholds, reclaimed segments, zoned GC tuning.
- Discard controls: request limits, issue timings, granularity, IO awareness, urgent utilization, pending/issued/queued discard counters.
- Node/segment manager tuning: IPU policy, NID read-ahead, dirty NAT ratio, SSR thresholds, reserved segments.
- Checkpoint controls: checkpoint interval and checkpoint thread IO priority.
- Compression counters and thresholds when configured.
- Atomic write counters.
- Extent cache age thresholds and read extent limits.
- Casefold encoding and effective lookup mode.
- Feature reporting for runtime-supported features and on-disk per-instance features.
- Fault injection rate/type/timeout when configured.
- Global cache donation tuning via `reclaim_caches_kb`.

## Store Validation
`__sbi_store` contains per-attribute validation rather than blindly writing offsets. It bounds discard, GC, compression, ATGC, fragmentation, extent, allocation, task-priority, and zoned-device values; wakes GC/discard threads for urgent modes; updates checkpoint thread IO priority; resets selected counters only when writing zero; and requires `CAP_SYS_NICE` for critical task priority changes.

## Procfs Diagnostics
Per-mount proc files include:
- `segment_info`
- `segment_bits`
- `victim_bits`
- `discard_plist_info`
- `disk_map`
- `donation_list`
- `inject_stats` when fault injection is enabled
- `iostat_info` when iostat is enabled elsewhere

These seq_file handlers dump segment state, victim section maps, discard pending-list distribution, on-disk layout, multi-device mappings, donated cache file state, and injected fault counters.

## Dependencies
- Uses F2FS core structures from `f2fs.h`, `segment.h`, `gc.h`, and `iostat.h`.
- Called from `super.c` during module init/exit and mount/unmount.
- Reads and mutates live `f2fs_sb_info`, segment manager, discard controller, GC thread, ATGC, checkpoint, and stat state.

## Notable Edge Cases
- GC-related stores take `s_umount` read lock using trylock and may return `-EAGAIN`.
- Several attributes are only present under Kconfig guards.
- Unregistration waits for kobject release completions to avoid use-after-free during unmount.

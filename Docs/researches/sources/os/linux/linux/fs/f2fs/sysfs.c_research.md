# File Research: sources/os/linux/linux/fs/f2fs/sysfs.c

Implements F2FS sysfs and procfs visibility/control surfaces.

Key behavior:
- Creates the global `/sys/fs/f2fs` kset, `/sys/fs/f2fs/features`, `/sys/fs/f2fs/tuning`, and `/proc/fs/f2fs`.
- For each mounted F2FS instance, registers:
  - `/sys/fs/f2fs/<sb-id>/`
  - `/sys/fs/f2fs/<sb-id>/stat/`
  - `/sys/fs/f2fs/<sb-id>/feature_list/`
  - `/proc/fs/f2fs/<sb-id>/`
- Defines `struct f2fs_attr` for per-superblock attributes and `struct f2fs_base_attr` for global feature/tuning attributes.
- Uses `__struct_ptr()` plus generated offset/size metadata to read and write fields from GC thread state, segment manager state, discard control, node manager state, `f2fs_sb_info`, fault-injection state, checkpoint request control, and ATGC state.
- Provides read-only show helpers for dirty/free/overprovisioned segments, lifetime writes, checkpoint status, discard state, ATGC state, GC mode, supported on-disk features, reserved/unusable blocks, encoding, lookup mode, mounted time, moved blocks, average valid blocks, defrag blocks, and main block address.
- Implements generic value show/store by field size for 1-, 2-, 4-, and 8-byte fields.
- Special-cases `extension_list` to display and update cold/hot extension lists under `sbi->sb_lock`, committing the superblock and rolling back the in-memory update if the commit fails.
- Special-cases `ckpt_thread_ioprio` to parse `rt,<level>` and `be,<level>`, update checkpoint-thread IO priority, and apply it to the running checkpoint thread when checkpoint merge is enabled.
- Special-cases fault-injection attributes to rebuild fault rate/type/timeout and optionally simulate lock timeout.
- Validates writes for discard controls, migration granularity, GC urgent/idle modes, GC remaining trials, zoned GC thresholds, iostat period, zoned allocation policy, compression counters and thresholds, ATGC ratios, GC segment mode, fragmentation knobs, atomic-write counters, extent age thresholds, read extent count, IPU policy, directory level, reserved pin sections, boosted GC knobs, background-GC IO awareness, allocation-section policy, lock-priority knobs, and critical task priority.
- Uses `s_umount` read locking for GC-related writes to avoid races with unmount.
- Exposes many generated attribute groups:
  - GC thread timings and boosting.
  - Segment manager IPU and reserved segment controls.
  - Discard command controls.
  - Node manager thresholds.
  - Superblock intervals, IO flags, read-ahead, fragmentation, compression, atomic write, extent cache, zoned, reserved pin, allocation, and lock-priority knobs.
  - Fault injection.
  - Checkpoint request control.
  - ATGC controls.
- Exposes global kernel-supported features as `/sys/fs/f2fs/features/*`, with conditional entries for encryption, block zoned, verity, casefold, compression, etc.
- Exposes per-filesystem on-disk feature support under `feature_list`, returning `supported` or `unsupported` for each feature bit.
- Implements `/sys/fs/f2fs/tuning/reclaim_caches_kb` to report donated cache size and trigger cache reclamation.
- Implements procfs single-file reports for:
  - `segment_info`
  - `segment_bits`
  - `victim_bits`
  - `discard_plist_info`
  - `disk_map`
  - `donation_list`
  - `inject_stats` when fault injection is enabled
  - `iostat_info` when iostat is enabled
- Proc reports expose detailed segment validity/type maps, SIT bitmaps/mtime, victim section bitmap, discard pending-list distribution, block address layout, multi-device map, donated-file cache state, and fault injection counts.
- Uses kobject release completions during unregister to ensure per-instance sysfs objects are fully released before teardown continues.

Important interactions:
- `super.c` calls `f2fs_init_sysfs()` at module init, `f2fs_register_sysfs()` during mount, `f2fs_unregister_sysfs()` during unmount/error cleanup, and `f2fs_exit_sysfs()` during module exit.
- Many sysfs writes directly affect runtime GC, discard, checkpoint, compression, iostat, zoned allocation, locking, and allocation behavior, so validation in this file is part of F2FS runtime safety.
- Procfs readers inspect live segment/discard/inode structures and use the mounted superblock as `seq_file` private data.

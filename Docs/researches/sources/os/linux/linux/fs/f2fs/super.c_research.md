# File Research: sources/os/linux/linux/fs/f2fs/super.c

Implements F2FS filesystem registration, mount/remount option parsing, superblock initialization and teardown, checkpoint state transitions, quota integration, encryption/verity/export hooks, and major superblock operations.

Key behavior:
- Defines the F2FS `file_system_type`, fs-context operations, `super_operations`, export operations, fscrypt operations, and module init/exit paths.
- Parses the full modern `fs_context` mount option set, including GC mode, discard, inline xattr/data/dentry, quota options, allocation/fsync modes, dummy encryption, inline crypto, checkpoint enable/disable/merge, compression, ATGC, discard unit, memory mode, error policy, NAT bits, and lookup mode.
- Tracks parsed option deltas through `f2fs_fs_context::opt_mask`, `spec_mask`, and `qname_mask`, then validates and applies them to `sbi->mount_opt`.
- Validates option consistency against device and on-disk features: readonly feature, zoned devices, discard requirements, device aliasing, quota feature state, dummy encryption, compression support, casefold/Unicode support, inline xattr sizing, LFS/ATGC incompatibility, and flush-merge/read-only constraints.
- Supplies default mount options and runtime defaults, including extent cache, discard defaults, active logs, inline features, checkpoint merge, lazytime, flush merge, fsync mode, compression defaults, memory mode, error policy, and lookup mode.
- Implements fault injection setup when enabled, including named fault types, rate/type/timeout updates, and lock-timeout simulation.
- Creates and destroys global caches/subsystems during module init/exit: inode cache, node/segment/checkpoint/recovery/extent/GC caches, sysfs, shrinker, stats, post-read processing, iostat, bio caches, bioset, compression pools/cache, casefold cache, and xattr cache.
- Provides inode lifecycle helpers:
  - `f2fs_alloc_inode()` initializes F2FS-specific inode state, dirty lists, semaphores, GC locks, xattr lock, compression and writeback counters.
  - `f2fs_drop_inode()` handles checkpoint-disabled meta/node inode dropping and avoids writeback/GC eviction deadlocks.
  - `f2fs_inode_dirtied()` and `f2fs_inode_synced()` maintain dirty inode accounting and atomic-write dirty state.
- Implements `put_super`, `sync_fs`, freeze/unfreeze, statfs, shutdown, and mount option display.
- `f2fs_put_super()` unregisters sysfs/proc entries, disables quota, stops checkpointing, writes unmount checkpoints when needed, drains discards, releases orphan/ino tracking, flushes writes, tears down compression/node/meta/segment managers, destroys stats and internal caches, frees options, unloads Unicode encoding, and invalidates block devices.
- `f2fs_sync_fs()` issues a checkpoint on synchronous sync unless checkpointing is disabled, a checkpoint error exists, or POR recovery is active.
- `f2fs_statfs()` reports block/inode capacity using user block count, valid user blocks, unusable block count, root reservations, and quota project limits when applicable.
- Implements checkpoint disable/enable:
  - Disabling checkpoint may force urgent foreground GC to reduce unusable blocks before writing a pause checkpoint.
  - Enabling checkpoint flushes dirty data/skipped writes, clears CP-disabled state, syncs the filesystem, and flushes pending checkpoint thread work.
- Implements remount through `__f2fs_remount()`, preserving old options for rollback and coordinating GC thread, flush-merge thread, discard thread, checkpoint state, checkpoint thread, quota suspend/resume, read-only transitions, and unsupported dynamic option changes.
- Implements quota support when configured:
  - Handles legacy quota file names and quota feature inodes.
  - Provides quota file read/write using pagecache operations.
  - Enables quota tracking from quota inodes or quota files.
  - Synchronizes, turns on/off, and marks quota repair flags after failures.
  - Provides `dquot_operations` and `quotactl_ops`.
- Registers fscrypt callbacks:
  - Stores encryption context in F2FS xattrs.
  - Rejects encrypting the root directory when lost+found is required.
  - Supplies dummy policy, stable inode, and multi-device lookup hooks.
- Registers fs-verity operations via `f2fs_verityops` when configured.
- Supplies NFS export file-handle translation through generic inode-number based helpers.
- Computes maximum file blocks from F2FS direct, indirect, and double-indirect node fanout, with an fscrypt IV data-unit compatibility cap.
- Reads both raw superblock copies, validates magic, checksum, block/sector geometry, segment layout, device segment totals, extension counts, checkpoint payload limits, reserved inode numbers, and metadata area boundaries.
- Repairs in-memory or on-disk superblock segment alignment when main-area end is smaller than segment-area end and writes are allowed.
- Validates checkpoint contents: metadata sizing, overprovision/reserved segments, user and valid block counts, node count, current segment numbers/offsets, duplicate current segments, SIT/NAT bitmap sizes, checksum layout, NAT bits payload space, and checkpoint error state.
- Initializes `f2fs_sb_info` geometry, counters, locks, intervals, GC and allocation policy, summary layout, node limits, dirty page counters, IO state, and lock-priority defaults.
- Handles zoned block devices by reporting zones, tracking sequential zones, enforcing single zone capacity, checking max open zones, and deriving zone geometry.
- Scans multi-device and zoned-device layouts, opens secondary block devices, maps per-device segment/block ranges, and records logical block-size alignment.
- Sets up casefold Unicode encoding from the superblock when available and rejects casefold filesystems without Unicode support.
- `f2fs_fill_super()` is the central mount path:
  - Allocates and initializes `sbi`.
  - Sets block size and reads/validates the raw superblock.
  - Applies mount options and superblock feature hooks.
  - Initializes IO, iostat, percpu counters, page-array cache, meta inode, checkpoint, device list, post-read workqueue, extent/ino/fsync tracking, checkpoint thread, segment manager, node manager, GC manager, stats, node inode, root inode/dentry, compression inode, sysfs, quota, orphan recovery, fsync recovery, write-pointer repair, in-memory current segments, checkpoint enable/disable, GC thread, and shrinker membership.
  - Has structured cleanup labels for every partially initialized subsystem and retries once after failed fsync recovery.
- Handles critical errors by setting checkpoint error flags, recording error/stop reasons asynchronously, applying `errors=` policy, optionally panicking, and preventing further updates.
- `kill_f2fs_super()` stops GC/discard, writes final checkpoints if needed, truncates compression cache, delegates to `kill_block_super()`, and frees device/sbi state after keyring teardown.

Important interactions:
- Mount option validation is tightly coupled to on-disk feature bits in `raw_super`, runtime state in `sbi`, and Kconfig-dependent support for quota, compression, encryption, zoned block devices, and Unicode.
- Superblock initialization wires together most other F2FS modules: node manager, segment manager, checkpoint, GC, recovery, xattr, verity, compression, iostat, and sysfs.
- Checkpoint-disabled mode affects inode dropping, statfs free-space reporting, remount behavior, quota flushing, and unmount cleanup.
- Error handling records stop reasons in the superblock through deferred work and informs fsck through SBI/CP flags.

# File Research: sources/os/linux/linux/fs/xfs/Kconfig

Defines XFS filesystem configuration options.

Key behavior:
- Declares `XFS_FS` as a block-device filesystem module/builtin option selecting `EXPORTFS`, `CRC32`, and `FS_IOMAP`.
- Defines deprecated-format support toggles:
  - `XFS_SUPPORT_V4` for old `crc=0` filesystems, default off, documented for removal in September 2030.
  - `XFS_SUPPORT_ASCII_CI` for deprecated ASCII case-insensitive filesystems, default off, also documented for removal in September 2030.
- Defines optional user-visible features:
  - `XFS_QUOTA`.
  - `XFS_POSIX_ACL`.
  - `XFS_RT`, defaulting to `BLK_DEV_ZONED`, for realtime subvolume and zoned device support.
- Defines internal feature gates:
  - `XFS_DRAIN_INTENTS`.
  - `XFS_LIVE_HOOKS`.
  - `XFS_MEMORY_BUFS`.
  - `XFS_BTREE_IN_MEM`.
- Defines online maintenance features:
  - `XFS_ONLINE_SCRUB`, requiring `TMPFS` and `SHMEM`, selecting live hooks, intent draining, and memory buffers.
  - `XFS_ONLINE_SCRUB_STATS`, requiring debugfs.
  - `XFS_ONLINE_REPAIR`, requiring online scrub and selecting in-memory btrees.
- Defines debug/warning controls:
  - `XFS_WARN`.
  - `XFS_DEBUG`.
  - `XFS_DEBUG_EXPENSIVE`.
  - `XFS_ASSERT_FATAL`.

Important interactions:
- `XFS_RT` is required for zoned block device support.
- Online repair depends on online scrub and enables additional btree infrastructure.
- V4 and ASCII-CI support are explicit compatibility/attack-surface choices.

# File Research: sources/os/linux/linux-stable/fs/ext4/ext4.h

## Summary
Central ext4 internal header. It defines ext4's on-disk metadata formats, in-memory inode and superblock state, mount and feature flags, allocator and mapping contracts, directory entry formats, error-reporting wrappers, and most cross-file function declarations used by the Linux stable ext4 implementation.

## Main Responsibilities
- Defines core ext4 scalar types: filesystem blocks, logical blocks, group numbers, and group-relative block offsets.
- Defines allocation inputs and flags for multiblock allocation, delayed allocation, bigalloc clusters, block freeing, and block mapping.
- Describes on-disk group descriptors, inodes, superblocks, directory entries, checksum tails, orphan-file blocks, and MMP blocks.
- Defines `struct ext4_inode_info` and `struct ext4_sb_info`, the main in-memory state containers for per-inode and per-mount ext4 behavior.
- Provides helpers for feature-bit testing and mutation, inode state/flag manipulation, size and timestamp encoding, block/group math, directory record sizing, and locking.
- Declares the public internal APIs implemented by ext4's allocation, inode, extent, directory, journaling, resize, orphan, inline-data, sysfs, block-validity, page-I/O, MMP, and verity files.

## Important Structures
- `struct ext4_allocation_request`: input to `ext4_mb_new_blocks()` and block allocator goal selection.
- `struct ext4_map_blocks`: logical-to-physical mapping result and request carrier for `ext4_map_blocks()` and query/create variants.
- `struct ext4_io_end` / `struct ext4_io_submit`: buffered writeback completion and bio aggregation state, especially for unwritten extent conversion.
- `struct ext4_group_desc`: on-disk block group descriptor, including low/high bitmap, inode table, free counts, flags, checksums, and exclude bitmap fields.
- `struct ext4_inode`: on-disk inode layout, including extents/indirect block storage, extended timestamps, checksums, version high bits, and project ID.
- `struct ext4_inode_info`: VFS inode wrapper with raw inode data, block group locality, xattr semaphore, orphan tracking, fast commit lists/ranges, `i_disksize`, `i_data_sem`, jbd2 inode, delayed allocation reservations, extent status tree, preallocations, inline-data offsets, quota state, completed I/O lists, fsync transaction IDs, checksum seed, project ID, and fscrypt state.
- `struct ext4_super_block`: on-disk superblock layout, including feature masks, journal metadata, group geometry, error history, quota inode numbers, checksum seed, encoding, orphan-file inode, and checksum.
- `struct ext4_sb_info`: in-memory superblock with geometry caches, group descriptors, counters, mount flags, journal/orphan state, mballoc caches and tunables, flex groups, lazy inode initialization, MMP, checksum seeds, shrinkers, xattr caches, journal triggers, error state, DAX state, atomic write units, and fast commit queues.

## Key Behavior
Feature handling is macro-generated through `EXT4_FEATURE_*_FUNCS()`, producing `ext4_has_feature_*`, `ext4_set_feature_*`, and `ext4_clear_feature_*` helpers over compatible, read-only-compatible, and incompatible superblock feature masks. Supported feature masks for ext2, ext3, and ext4 are defined in this header.

Inode flags are represented both as on-disk `EXT4_*_FL` masks and bit indices such as `EXT4_INODE_EXTENTS`. `ext4_check_flag_values()` enforces that these remain consistent at build time. Dynamic inode state bits share storage with `i_flags` on 64-bit builds and use `i_state_flags` on smaller word-size builds.

Timestamp helpers encode and decode ext4's extra epoch and nanosecond fields, falling back to clamped 32-bit seconds when a legacy inode lacks enough extra space.

Directory definitions cover legacy and `file_type` entries, encrypted+casefolded hash suffixes, checksum tails, record-length encoding for block sizes up to 256 KiB, htree hash versions, and link-count behavior for indexed directories.

The header centralizes error paths: `ext4_error*`, `ext4_warning*`, `ext4_msg`, `ext4_abort`, and group-locked error wrappers attach caller location, inode/file/block context, and optional errno to superblock error accounting.

## Synchronization and Lifetime
`i_data_sem` serializes extent/indirect tree mutation against truncate and uses lock subclasses for normal, second-inode, quota, and EA-inode cases. `xattr_sem` separates extended attribute reads/writes from regular data `i_rwsem` traffic. `s_writepages_rwsem` protects writeback against remount or inode flag changes that alter journaling, delayed allocation, DAX, or direct-I/O behavior. Fast commit queues are protected by `s_fc_lock` with NOFS wrappers.

RCU is used for resizable arrays such as group descriptors, group info, and flex groups. Group locks come from `blockgroup_lock`, with contention tracking used by the allocator.

## Dependencies
Includes JBD2, quotas, fscrypt, fsverity, percpu counters, block devices, FIEMAP, rbtree, seqlock, and ext4 subheaders `extents_status.h` and `fast_commit.h`. It is included by most ext4 implementation files and is the shared contract between allocator, extent, journaling, inode, directory, resize, and recovery logic.

## Risks
This header encodes ABI-sensitive on-disk layouts and feature masks; any change must preserve endian handling, struct offsets, and compatibility with e2fsprogs and older kernels. Many inline helpers assume the caller already holds the right inode, group, journal, or resize locks. Size, timestamp, cluster, and block-number helpers are easy to misuse across bigalloc, 64-bit, non-extent, and large-directory cases.

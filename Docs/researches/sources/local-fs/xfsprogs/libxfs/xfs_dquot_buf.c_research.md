# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dquot_buf.c

## Purpose
Implements on-disk quota record verification, repair initialization, quota buffer verifiers, quota timer conversion, and quota metadata inode loading/creation helpers.

## Main Entry Points
- `xfs_calc_dquots_per_chunk()` derives quota records per buffer chunk.
- `xfs_dquot_verify()` validates a single `xfs_disk_dquot`.
- `xfs_dqblk_verify()` validates the containing `xfs_dqblk`, including UUID for CRC filesystems.
- `xfs_dqblk_repair()` zeroes and initializes a quota block for quotacheck repair.
- `xfs_dquot_buf_ops` and `xfs_dquot_buf_ra_ops` provide normal and readahead buffer verifier operations.
- `xfs_dquot_from_disk_ts()` and `xfs_dquot_to_disk_ts()` convert quota grace timers, including bigtime encoding.
- `xfs_dqinode_load()`, `xfs_dqinode_metadir_create()`, `xfs_dqinode_metadir_link()`, `xfs_dqinode_mkdir_parent()`, and `xfs_dqinode_load_parent()` manage quota inodes in legacy superblock fields or the metadata directory.

## Internal Mechanics
Quota verification checks magic, version, type mask, record type, bigtime feature compatibility, expected id, and consistency between soft limits, current usage, and timers. Buffer verification first checks per-record CRCs on CRC filesystems, then verifies monotonically increasing ids across all quota records in the buffer. Readahead failures are quiet: the buffer is marked not done so a real read can perform full reporting.

Quota inode loading supports old filesystems with superblock quota inode numbers and newer metadir filesystems where quota files live under `/quota`.

## Dependencies
Depends on quota definitions, transaction and inode helpers, filesystem health flags, metadir/metafile APIs, checksum helpers, and endian conversion utilities.

## Risks and Notes
The verifier intentionally tolerates some uninitialized quota-buffer scenarios by reporting structural failure without assuming quota loss. `xfs_dqinode_load()` marks the relevant quota metadata sick when loading detects metadata errors or invalid quota inode formats. Userspace-only `xfs_dqinode_metadir_link()` is excluded under `__KERNEL__`.

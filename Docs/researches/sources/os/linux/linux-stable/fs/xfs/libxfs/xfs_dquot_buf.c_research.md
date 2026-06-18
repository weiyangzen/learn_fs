# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dquot_buf.c

## Purpose

`xfs_dquot_buf.c` implements on-disk quota record verification/repair, dquot buffer verifier operations, quota timer conversion, quota inode loading, and metadata-directory quota inode helpers.

## Dquot Verification and Repair

- `xfs_calc_dquots_per_chunk` derives the number of `struct xfs_dqblk` records in a buffer measured in basic blocks.
- `xfs_dquot_verify` validates the embedded `xfs_disk_dquot`: magic, version, type bits, quota record type, bigtime compatibility, id consistency, and soft-limit timer consistency.
- `xfs_dqblk_verify` adds v5 UUID checking before calling `xfs_dquot_verify`.
- `xfs_dqblk_repair` zeroes a dquot block and rebuilds magic/version/type/id/uuid/checksum fields, primarily for quotacheck-driven repair.

The verifier explicitly tolerates uninitialized quota blocks by returning corruption only when the expected dquot magic is absent to callers that know whether to complain. Comments explain recovery cases where quota blocks can legitimately be uninitialized after crash or quotaoff replay.

## Buffer Operations

`xfs_dquot_buf_verify_crc` validates the CRC of every dquot record in a quota buffer when CRCs are enabled. It computes the record count from `m_quotainfo` if available, or from buffer length during log recovery before quota state exists.

`xfs_dquot_buf_verify` checks each dquot in sequence and assumes ids increase monotonically from the first record's id. This means corruption of the first id can cause a later record to be where the verifier notices the mismatch.

The exported buffer ops are:

- `xfs_dquot_buf_ops`: normal read/write/struct verifier.
- `xfs_dquot_buf_ra_ops`: readahead verifier that reports failures silently by setting `-EIO` and clearing `XBF_DONE`, so a later real read can retry and report through normal verifier paths.

Write verification checks structure only; CRC calculation is intentionally done when the dquot is flushed into the buffer so that in-buffer dquot CRCs stay current.

## Time Conversion

`xfs_dquot_from_disk_ts` and `xfs_dquot_to_disk_ts` convert quota grace timers between on-disk 32-bit values and in-core `time64_t`, using bigtime conversion when the dquot type carries `XFS_DQTYPE_BIGTIME`.

## Quota Inode Loading and Health

`xfs_dqinode_sick_mask` maps user/group/project quota types to filesystem health bits. `xfs_dqinode_load` loads the quota inode either from legacy superblock inode numbers or from the metadata directory, validates the inode fork format is extents or btree, checks project id zero, and marks the appropriate quota health bit sick on metadata corruption.

## Metadata Directory Helpers

For filesystems with metadir support:

- `xfs_dqinode_metadir_create` creates a quota metadata file under the quota metadir and finishes inode setup.
- `xfs_dqinode_metadir_link` exists for userspace builds (`!__KERNEL__`) to link an existing quota inode.
- `xfs_dqinode_mkdir_parent` creates the `/quota` metadata directory under the filesystem metadir.
- `xfs_dqinode_load_parent` loads that `/quota` parent directory even when quotas are not enabled, supporting operations such as quota removal.

## Dependencies and Interactions

This file is used by quota runtime code, quota log item recovery, generic buffer item recovery, and quota manager paths. It depends on XFS health tracking, metadir/metafile helpers, quota type helpers, buffer verifier infrastructure, and transaction inode logging.

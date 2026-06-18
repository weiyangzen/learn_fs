# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dquot_buf.c

## Purpose

Implements XFS quota dquot buffer verification, repair initialization, buffer verifier operations, quota timer conversion, quota health mask mapping, and loading/creating metadata quota inodes either from legacy superblock inode fields or the metadata directory hierarchy.

## Main Interfaces

- Dquot sizing and verification: `xfs_calc_dquots_per_chunk()`, `xfs_dquot_verify()`, `xfs_dqblk_verify()`, `xfs_dqblk_repair()`.
- Buffer ops: `xfs_dquot_buf_ops`, `xfs_dquot_buf_ra_ops`, internal CRC/struct read/write/readahead verifiers.
- Timer conversion: `xfs_dquot_from_disk_ts()`, `xfs_dquot_to_disk_ts()`.
- Health mapping: `xfs_dqinode_sick_mask()`.
- Quota inode access: `xfs_dqinode_load()`, `xfs_dqinode_metadir_create()`, userspace-only `xfs_dqinode_metadir_link()`, `xfs_dqinode_mkdir_parent()`, `xfs_dqinode_load_parent()`.

## Control Flow And Behavior

Dquot verification checks magic, version, type mask and record type, bigtime feature compatibility, bigtime id constraints, expected id when supplied, and quota soft-limit timer invariants. Disk quota block verification also checks the metadata UUID on CRC-enabled filesystems. Repair zeroes the whole dquot block, writes magic/version/type/id, and writes UUID/checksum when needed.

Buffer CRC verification walks all dquots in a buffer, using quota-info `qi_dqperchunk` when available and falling back to chunk-size calculation during log recovery. Structural verification expects monotonically increasing ids within the buffer, starting from the first dquot id. Normal read verification reports CRC or corruption through buffer verifier errors; readahead verification is silent and marks the buffer `!DONE` with `-EIO` so a later real read re-verifies it. Write verification checks structure but leaves CRC calculation to dquot flush.

Timer conversion supports legacy second-based timers and bigtime-encoded quota timers based on the dquot type flag. Quota inode loading uses legacy superblock quota inode numbers on non-metadir filesystems and named metadata directory lookups when metadir is enabled. Loaded quota inodes are checked for acceptable data fork formats and zero project id; metadata corruption marks the corresponding quota health bit.

Metadata directory helpers create or load the `/quota` directory and quota files, committing metadata directory update transactions and finishing inode setup after creation.

## State And Data Structures

On-disk quota buffers contain repeated `struct xfs_dqblk`, each embedding `struct xfs_disk_dquot` plus optional CRC metadata. Quota inode locations are either superblock fields (`sb_uquotino`, `sb_gquotino`, `sb_pquotino`) or metadata directory entries under `/quota`.

## Dependencies

Depends on quota manager state, CRC helpers, buffer verifier infrastructure, metadata inode loading, metadir/metafile helpers, transaction inode logging, and filesystem health reporting.

## Risks And Invariants

- Readahead verification must remain silent and leave final reporting to a normal read.
- During log recovery, verifier logic cannot assume quota subsystem initialization.
- Dquot ids within a verified buffer are assumed to increase from the first id; corruption of the first id can shift reported failure location.
- Bigtime dquot flags are invalid unless the filesystem supports bigtime.
- Quota inode loading must mark the correct quota health bit on metadata corruption.

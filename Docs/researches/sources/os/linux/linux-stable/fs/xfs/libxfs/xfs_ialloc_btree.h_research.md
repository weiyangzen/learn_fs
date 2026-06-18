# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.h

## Role in the repository

`xfs_ialloc_btree.h` declares the INOBT/FINOBT btree format helpers and public btree support API. It bridges on-disk inode allocation record layout from `xfs_format.h` with the generic btree engine.

## Layout macros

`XFS_INOBT_BLOCK_LEN` selects the correct short-form btree header length based on whether the filesystem has CRC metadata.

Address macros compute one-based record, key, and pointer locations inside an INOBT/FINOBT block:
- `XFS_INOBT_REC_ADDR`
- `XFS_INOBT_KEY_ADDR`
- `XFS_INOBT_PTR_ADDR`

The comments note that some macros are used by userspace even if they appear unused in kernel-only analysis.

## Public API

The header declares:
- cursor constructors for INOBT and FINOBT;
- fanout calculation via `xfs_inobt_maxrecs`;
- sparse record holemask-to-allocation-mask conversion;
- optional debug count validation;
- FINOBT reservation calculation;
- INOBT/FINOBT btree size calculation;
- staged btree commit;
- maximum on-disk height calculation;
- cursor cache init/destroy.

## Important invariants

- INOBT and FINOBT use the same record, key, and pointer block layout.
- Header length depends on CRC support and must be subtracted before fanout calculations.
- Address macros assume one-based btree indexes, matching the generic XFS btree engine.
- Staged btree commit is the repair/rebuild path for replacing AGI roots.

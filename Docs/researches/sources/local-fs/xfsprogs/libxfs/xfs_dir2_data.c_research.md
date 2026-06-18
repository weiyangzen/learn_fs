# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_data.c

## Purpose
Implements shared XFS directory data-block handling for block, leaf, and node directory formats. It validates v2/v3 directory data buffers, initializes new data blocks, tracks the three-entry `bestfree` table, logs directory data changes, and converts byte ranges between active dirents and unused records.

## Main Entry Points
- `xfs_dir2_data_bestfree_p()` abstracts the v2/v3 header layout difference for the best-free table.
- `xfs_dir2_data_entry_tag_p()`, `xfs_dir2_data_get_ftype()`, and `xfs_dir2_data_put_ftype()` handle variable-size data entries.
- `__xfs_dir3_data_check()` performs structural verification of data and block-format directory buffers.
- `xfs_dir3_data_read()` and `xfs_dir3_data_readahead()` read/readahead data blocks with buffer verifiers and owner checks.
- `xfs_dir3_data_init()` allocates and initializes a new directory data block.
- `xfs_dir2_data_freefind()`, `xfs_dir2_data_freeinsert()`, `xfs_dir2_data_freescan()`, `xfs_dir2_data_make_free()`, and `xfs_dir2_data_use_free()` maintain free-space records.
- `xfs_dir2_data_log_entry()`, `xfs_dir2_data_log_header()`, and `xfs_dir2_data_log_unused()` log precise byte ranges into the transaction.
- `xfs_dir3_data_end_offset()` returns the end of the dirent area for data vs block-format buffers.

## Internal Mechanics
The verifier checks magic values, CRC-era UUID/block/LSN metadata, owner fields, sorted bestfree entries, unused-record tags, non-overlap, dirent inode validity, filetype validity, block-format leaf references, sorted block leaf hashes, and stale counts. The same low-level checker supports pure data blocks and block-format directories because both share dirent/free-record layout before the leaf/tail area.

Free-space mutation is local and careful: `make_free` merges with previous and/or following unused records and either updates the bestfree table directly or asks for a full rescan; `use_free` carves allocation from the front, back, middle, or whole unused record. Both paths report whether callers must log the header and whether the bestfree table needs reconstruction.

## Dependencies
Depends on XFS directory geometry, transaction logging, buffer verification/checksum helpers, inode health marking, endian helpers, and shared directory APIs from `xfs_dir2.h` / `xfs_dir2_priv.h`. It is used by block, leaf, node, and shortform conversion code.

## Risks and Notes
The code is metadata-critical: almost every caller relies on bestfree correctness to avoid directory corruption. Many functions assume the caller has already validated alignment and range choices; the defensive checks in `xfs_dir2_data_use_free()` are therefore important. Any format change affecting dirent size, ftype storage, CRC headers, or block-format tails must be reflected here and in all callers that calculate offsets.

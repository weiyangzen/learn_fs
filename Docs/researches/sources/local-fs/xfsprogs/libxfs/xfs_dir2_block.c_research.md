# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_block.c

## Purpose

`xfs_dir2_block.c` implements single-block XFS directory operations: block verification, lookup, add, remove, replace, conversion from shortform to block, and conversion from leaf back to block.

## Main Behavior

The file initializes cached hashes for `.` and `..`, defines v2/v3 block buffer ops, verifies magic, CRC, uuid, physical block number, log sequence number, owner, and full data-block structure, and stamps v3 block headers during initialization.

A block directory stores data entries at the front and an embedded sorted leaf array plus tail at the end. `xfs_dir2_block_addname` reads the only block, determines whether data and leaf space exist, reuses stale leaf entries when possible, compacts stale entries when useful, or converts to leaf format when the block cannot fit another entry. Insertions binary-search the hash position, allocate data-entry space from bestfree, fill inode/name/filetype/tag fields, update the embedded leaf entry, log affected ranges, and validate the result.

`xfs_dir2_block_lookup_int` binary-searches the embedded leaf array by hash, scans duplicate hashes, skips stale entries, compares names with normal or ASCII-CI comparison, and preserves a case-insensitive match while continuing to look for an exact match. Public lookup returns inode number, filetype, and optional actual CI name.

Removal finds the entry, frees the data-entry space, marks the leaf entry stale with `XFS_DIR2_NULL_DATAPTR`, updates tail stale count, rescans bestfree if needed, and converts back to shortform when the resulting directory fits in the inode. Replacement changes the inode number and filetype in place.

`xfs_dir2_leaf_to_block` compacts a single-leaf directory back into block format when only the first data block remains and the embedded leaf/tail area fits. It trims trailing empty data blocks, initializes the data block as a block directory, copies non-stale leaf entries, frees the old leaf block, and may then shrink further to shortform. `xfs_dir2_sf_to_block` converts inline shortform directories into a new block: it allocates block zero, creates `.` and `..`, preserves existing shortform offsets by inserting free holes, copies all entries, builds and sorts the embedded leaf array, and logs the block.

## Dependencies and Risks

This file depends on data-block free-space management, shortform helpers, leaf-format conversion helpers, da block allocation/shrink, transaction logging, CRC buffer ops, directory hashing/comparison, and geometry offset helpers. Risks include stale leaf compaction boundaries, bestfree consistency after split/free operations, preserving shortform offsets during conversion, duplicate-hash lookup order, no-reservation conversion failures, and ensuring block-to-shortform decisions use exact packed size calculations.

# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_block.c

## Scope

This file implements the XFS single-block directory format: block verification, initialization, lookup, add, remove, replace, logging of embedded leaf/tail regions, conversion from shortform to block, and conversion from leaf back to block when possible.

## Main Interfaces

- Startup: `xfs_dir_startup()` precomputes hashes for `.` and `..`.
- Verification and buffer ops: `xfs_dir3_block_buf_ops`, `xfs_dir3_block_header_check()`, `xfs_dir3_block_read()`.
- Block initialization: internal `xfs_dir3_block_init()`.
- Single-block operations: `xfs_dir2_block_addname()`, `xfs_dir2_block_lookup()`, `xfs_dir2_block_removename()`, `xfs_dir2_block_replace()`.
- Conversion: `xfs_dir2_leaf_to_block()`, `xfs_dir2_sf_to_block()`.
- Internal helpers: block space selection, leaf compaction, leaf/tail logging, lookup implementation, and leaf-entry sort comparator.

## Control Flow And Behavior

Block verifiers check magic, CRC metadata, UUID, block address, LSN, and data block structural consistency. `xfs_dir3_block_read()` reads the one data block, validates the owner for CRC filesystems, marks the buffer type, and marks directory health sick on corruption.

Adding a name reads the block, determines whether there is room for both a data entry and leaf entry, optionally compacts stale embedded leaf entries, binary-searches the leaf array by hash, inserts or reuses a leaf slot, allocates free space for the data entry, writes inode/name/filetype/tag, updates bestfree, and logs modified ranges. If no room exists and the caller has space reservation, it converts the directory to leaf format and retries there; if the call was only a space check it returns `-ENOSPC` or success without modification.

Lookup binary-searches the embedded leaf array, backs up to the first duplicate hash, scans forward through matching hashes, skips stale entries, compares names with normal or ASCII case-insensitive comparison, and returns the inode/filetype plus optional CI actual name.

Removal marks the data entry free, marks the leaf address stale, updates tail stale count, rescans bestfree if needed, and then tests whether the directory now fits in shortform. If it fits, it converts block format to shortform.

Replacement finds the entry and updates only the inode number and filetype in the data entry.

Leaf-to-block conversion succeeds only when the directory has no extra nonempty data blocks and the first data block has enough trailing free space to embed the leaf entries and tail. It initializes the block header, compacts out stale leaf entries, frees the old leaf block, and may further shrink to shortform.

Shortform-to-block conversion copies the in-inode directory to a temporary buffer, converts the data fork to extents, allocates block zero, initializes data/block headers, creates `.` and `..`, recreates all shortform entries at their preserved offsets, fills holes as unused entries, sorts leaf entries by hash, and logs the new block.

## State And Data Structures

- Single-block directories are a data block with active/unused entries at the front and an embedded sorted leaf array plus `xfs_dir2_block_tail` at the end.
- Tail fields track leaf entry count and stale count.
- Directory data bestfree tracks the largest free regions used to choose insertion space.
- Precomputed dot/dotdot hashes are used during shortform-to-block conversion.

## Dependencies

Depends on directory data helpers, DA buffer reads, bmap conversion from local to extents, leaf format conversion code, transaction logging, CRC buffer verification, and directory health marking.

## Risks And Invariants

- Embedded leaf entries must remain sorted by hash and must preserve duplicate-hash lookup behavior.
- Stale leaf entries and free data regions are separate accounting systems; compaction must update both correctly.
- Add paths must reserve room for both the data entry and the embedded leaf entry.
- Shortform-to-block conversion preserves shortform offsets by creating holes where needed.
- Conversion fallback decisions affect ENOSPC behavior and must respect whether the caller supplied a space reservation.

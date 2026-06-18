# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_block.c

## Role
`xfs_dir2_block.c` implements XFS single-block directory format operations. In this format, directory data entries and a compact leaf index live together in one directory block.

## Main Responsibilities
- Initialize cached hashes for `.` and `..`.
- Verify, read, initialize, and type single-block directory buffers.
- Add, lookup, remove, and replace entries in block-format directories.
- Manage embedded leaf entries, stale entries, block tails, and data free space.
- Convert block directories to/from shortform and leaf formats.

## Important Functions
- `xfs_dir_startup` precomputes hash values for `.` and `..`.
- `xfs_dir3_block_verify`, read/write verifiers, and `xfs_dir3_block_buf_ops` validate magic, CRC metadata, LSN, UUID, block number, and internal data layout.
- `xfs_dir3_block_read` reads the single directory data block, checks owner metadata for v3 blocks, marks sick state on corruption, and sets transaction buffer type.
- `xfs_dir3_block_init` stamps v2 or v3 block headers and initializes verification metadata.
- `xfs_dir2_block_need_space` determines whether a new data entry can fit by reusing stale leaf entries, using bestfree space, or compacting.
- `xfs_dir2_block_compact` compacts embedded leaf entries while intentionally leaving one stale entry available.
- `xfs_dir2_block_addname` inserts a name by checking space, possibly converting to leaf format, finding the sorted hash position, reusing stale entries or allocating tail leaf space, consuming data free space, writing the dirent, and logging touched ranges.
- `xfs_dir2_block_lookup` and `xfs_dir2_block_lookup_int` binary-search the embedded leaf index by hash and then scan duplicate hashes for an exact or case-insensitive name match.
- `xfs_dir2_block_removename` frees the data entry, marks the leaf index stale, updates bestfree information, and converts to shortform if the result fits in the inode fork.
- `xfs_dir2_block_replace` updates a matched entry's inode number and file type.
- `xfs_dir2_leaf_to_block` converts a single-leaf directory back to block format when all data fits in the first data block and sufficient tail space exists.
- `xfs_dir2_sf_to_block` expands an inode-local shortform directory into an allocated block with `.` and `..` entries, preserved offsets, free holes, and sorted leaf entries.

## Data Layout
- The block starts as a directory data block and ends with `struct xfs_dir2_block_tail`.
- Embedded leaf entries grow backward from the tail area, while directory data entries and unused regions occupy the data area.
- Leaf entries are sorted by hash and point to data entries through directory dataptrs.
- Stale leaf entries are represented by `XFS_DIR2_NULL_DATAPTR`.

## Invariants
- The verifier delegates detailed data layout checking to `__xfs_dir3_data_check`.
- Adds preserve sorted hash order and handle duplicate hashes.
- Directory data entry tags store the entry's starting offset and are logged with the entry.
- Conversion from shortform preserves existing shortform offsets by inserting explicit unused entries where needed.
- Conversion from leaf to block is only allowed when trailing data blocks can be trimmed and the leaf index fits into free space at the end of the first data block.

## Error Handling
- Header or verifier corruption returns `-EFSCORRUPTED`, marks buffers corrupt, and marks the directory data fork sick.
- Space-only checks return `-ENOSPC` without modifying the buffer.
- If a block-format add cannot fit and the caller has a reservation, the directory converts to leaf format and retries through `xfs_dir2_leaf_addname`.

## Dependencies
This file depends on DA buffer reads, directory data free-space helpers, shortform conversion helpers, leaf conversion helpers, transaction range logging, buffer verifier infrastructure, and directory health marking.

## Research Notes
The single-block directory code is a dense in-block allocator plus sorted hash index. Most subtlety comes from balancing three movable areas in one buffer: variable-length dirents, reusable free regions, and a reverse-growing embedded leaf table.

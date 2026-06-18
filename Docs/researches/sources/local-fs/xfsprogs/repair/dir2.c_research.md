# File Research: sources/local-fs/xfsprogs/repair/dir2.c

## Role

`dir2.c` validates and performs limited repair of XFS v2/v3 directory formats during inode processing. It supports shortform, block, leaf, and node directories. Its output feeds inode discovery, parent tracking, dot/dotdot repair decisions, and later directory rebuilding.

## Bad Directory Tracking

The file maintains a process-wide locked list of directory inode numbers whose leaf/node linkage is known bad. `dir2_is_badino` lets future passes avoid repeatedly traversing known-bad leaf/node btrees.

## Shortform Directories

`process_sf_dir2` validates inline directory data stored in the inode data fork. It checks and repairs:

- Entry count consistency.
- `i8count` consistency and conversion from 64-bit inode encoding back to compact encoding when possible.
- Directory size versus actual encoded entries.
- Entry offsets and regenerated legal offsets.
- Invalid, self-referential, special metadata, free, or nonexistent child inode references.
- Illegal names and zero-length names.
- Parent pointer validity.

During inode discovery it adds valid but unknown child inodes to the uncertain inode tree. Outside discovery, unknown or free entries are junked.

Special handling:

- Shortform directories do not store explicit `.` or `..` entries; the parent inode is in the header.
- Root `..` is corrected to self.
- Non-root self-parenting is cleared for later phase 6 reconstruction.
- Metadata directories are always rebuilt, so child inode state is not used to reject entries.

## Block Directories

`process_block_dir2` reads the single directory block via the inode `blkmap`, validates block magic, bounds the leaf array against the tail, processes the data area, and marks buffers dirty if fixups or checksum recomputation are needed.

## Directory Data Blocks

`process_dir2_data` is the common validator for longform directory data blocks. It:

- Verifies free-space entries, data-entry tags, alignment, and bestfree ordering.
- Rejects structurally corrupt blocks so later phases can rebuild or junk them.
- Validates child inode numbers.
- Marks bad entries by replacing the first name byte with `/`, which makes them recognizable for later cleanup.
- Preserves `.` and `..` long enough for special correction logic.
- Corrects bad `.` inode numbers.
- Detects and clears duplicate `.` or `..`.
- Rejects non-dot entries that point to the containing directory.
- Repairs bestfree tables with `libxfs_dir2_data_freescan`.

## Leaf and Node Directories

`process_leaf_block_dir2` validates leaf block entry count, stale count, and hash ordering.

`process_leaf_level_dir2` walks leaf blocks left to right, verifies sibling back pointers, validates parent btree paths with `verify_da_path`, and checks the final rightmost path with `verify_final_da_path`.

`process_node_dir2` traverses the directory btree to the leftmost leaf, then delegates leaf walking and parent path verification.

`process_leaf_node_dir2` scans all mapped data blocks below the leaf area and then, for node directories, verifies the leaf/node btree unless the directory is already known bad.

## Public Entrypoint

`process_dir2` chooses the processing path from inode format and final file block offset:

- Local format and size within inode fork: shortform.
- One directory block: block format.
- Blocks extending into leaf/node region: leaf/node format.
- Anything else: invalid size/format.

It reports missing `.` and `..` entries. Missing root or metadata-root `..` sets global repair flags so later phases can recreate them.

## Interactions

- Uses inode trees from `incore` to decide whether referenced inodes exist, are confirmed, or are free.
- Adds unknown directory references to uncertain inode lists during phase 3 discovery.
- Uses `blkmap` and `da_read_buf` to read directory blocks.
- Cooperates with phase 6 by marking bad entries and deferring graph-level dot/dotdot reconstruction.
- Checks global quota, realtime, rtrmap, rtrefcount, and metadata root inode identities so user directories cannot retain special metadata references.

## Repair Model

Directory repair here is intentionally local. It fixes obvious encoding and entry problems, but does not fully rebuild directory topology. Parent/child graph consistency and dot/dotdot reconstruction happen later when all inode references are known.

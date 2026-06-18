# File Research: sources/local-fs/ocfs2-tools/libocfs2/inode_scan.c

Implements full inode scanning across global and per-slot inode allocator files.

Main structure:
- `_ocfs2_inode_scan` tracks the filesystem, cached inode allocator inodes, current chain/group descriptor, buffered group blocks, block offsets, and state for discontiguous block groups.
- The scan includes one global inode allocator plus one inode allocator per slot: `s_max_slots + 1`.

Scan flow:
- `ocfs2_open_inode_scan()` allocates scan state, loads global inode alloc and each slot inode alloc through system-inode lookup, and allocates a 4 MiB group buffer sized in filesystem blocks.
- `ocfs2_get_next_inode()` returns the next raw inode block plus its block number. It does not validate the inode signature or swap the inode; callers do that after filtering.
- `ocfs2_close_inode_scan()` releases cached allocator inodes, group buffer, descriptor buffer, and scan state.
- `ocfs2_get_max_inode_count()` sums cluster counts of inode allocator files and converts to blocks.

Allocator traversal:
- `get_next_inode_alloc()` advances to the next non-empty inode allocator.
- `get_next_chain()` selects the next chain record from the inode allocator chain list.
- `get_next_group()` reads the current group descriptor, validates `bg_blkno`, skips the descriptor block, and initializes group bitmap offsets.
- `get_next_read_blocks()` supports both contiguous and discontiguous group descriptors. For discontiguous groups it walks extent records and adjusts `cur_blkno` when moving to a new record.
- `fill_group_buffer()` orchestrates transitions between chains, groups, and buffered reads.

Error and corruption handling:
- Uses `abort()` for internal state violations that should be impossible if callers obey the iterator contract.
- Returns `OCFS2_ET_CORRUPT_GROUP_DESC` or `OCFS2_ET_CORRUPT_CHAIN` for on-disk inconsistency.
- End-of-scan is indicated by `*blkno = 0` with success.

Dependencies and interactions:
- Used by quota usage computation and debug scanning paths.
- Depends on system inode lookup, cached inode reads, group descriptor reads, block reads, and cluster/block conversion.
- Includes support for discontiguous block groups, matching the feature documented in `ocfs2.7.in`.

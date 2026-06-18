# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_htree.c

This file implements ext2 htree indexed-directory lookup and contains code for htree index creation and insertion/splitting. In this DragonFlyBSD source, the normal `ext2_direnter` path has htree insertion/index creation compiled out because of a documented lost-dirent issue, but existing indexes can still be used for lookup.

Key responsibilities:
- Detect indexed directories.
- Traverse htree root and optional second-level nodes to find candidate leaf blocks.
- Search candidate leaf directory blocks, including collision continuation.
- Create a new htree index from a one-block linear directory.
- Split full directory data blocks by name hash and insert new index entries.
- Split index nodes and create a second level when needed.
- Maintain directory and htree checksums.

Important functions:
- `ext2_htree_has_idx`: Checks directory hash-index feature plus inode `IN_E3INDEX`.
- `ext2_htree_find_leaf`: Reads root block, validates hash version and limits, computes name hash, binary-searches htree entries, and records traversal path.
- `ext2_htree_lookup`: Finds candidate leaf blocks and calls `ext2_search_dirblock`; follows collision chains with `ext2_htree_check_next`.
- `ext2_htree_append_block`: Appends a full directory block through `VOP_WRITE`.
- `ext2_htree_writebuf`: Writes all index buffers after setting htree checksums.
- `ext2_htree_split_dirblock`: Sorts entries by hash, moves roughly half to a new block, chooses split hash, handles collision bit, appends the new entry, and initializes dirent tails.
- `ext2_htree_create_index`: Rewrites block 0 as an htree root and appends two data blocks.
- `ext2_htree_add_entry`: Splits target leaf blocks and, if needed, index nodes.

Important interactions:
- Uses `ext2_htree_hash`, `ext2_blkatoff`, `ext2_search_dirblock`, `ext2_dirent_csum_set`, and `ext2_dx_csum_set`.
- Lookup is called from `ext2_lookup.c`.

Notable behavior and risks:
- HTree mutation code exists but is disabled in `ext2_direnter` with an explicit comment documenting reproducible lost entries.
- `ext2_htree_add_entry` falls back to linear `ext2_add_entry` when `ip->i_count != 0`, meaning lookup slot accounting can bypass splitting.
- Only up to one level of indirection is accepted by `ext2_htree_find_leaf`.

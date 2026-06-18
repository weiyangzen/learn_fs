# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/htree.c

This file implements ext3 directory helper logic, including htree indexed directory hashing, lookup, readdir, insertion, splitting, linear fallback, deletion, and empty-directory checks. It is Linux ext3 code adapted to the Ext2Fsd/ReactOS buffer-head and IRP-context environment.

Key responsibilities:
- Provide ext3 directory hash functions and htree index traversal under `EXT2_HTREE_INDEX`.
- Read metadata directory blocks through Ext2Fsd mapping paths.
- Add, find, delete, and validate ext3 directory entries.
- Convert one-block linear directories into indexed htree directories.
- Split full directory leaf/index blocks during insertion.
- Feed htree directory results to Windows directory enumeration in stable hash order.
- Maintain directory link counts, file type bytes, times, and inode dirty state.

Important functions:
- `half_md4_transform`, `TEA_transform`, legacy hash helpers, `str2hashbuf_*`, `ext3_dirhash`: Implement ext3 legacy, half-MD4, and TEA filename hash algorithms.
- `ext3_current_time`, `ext3_warning`: Time conversion and debug-only warning reporting.
- `ext3_bread`: Maps a directory logical block through extents or indirect mapping and reads the metadata block into a buffer head.
- `ext3_append`: Extends a directory by one filesystem block via `Ext2ExpandFile`, updates FCB/MCB sizes, saves the inode, and returns the new block.
- `ext3_inc_count`, `ext3_dec_count`, `ext3_type_by_mode`, `ext3_set_de_type`, `ext3_mark_inode_dirty`, `ext3_update_dx_flag`: Small inode and directory-entry metadata helpers.
- `add_dirent_to_buf`: Inserts a dirent into an existing free slot or split record, checks for duplicates, updates directory times/version, marks inode and buffer dirty, and releases the buffer except on `-ENOSPC`.
- `dx_probe`, `dx_release`, `ext3_htree_next_block`: Validate and traverse htree root/node entries to locate leaf blocks.
- `ext3_htree_store_dirent`, `free_rb_tree_fname`, `create_dir_info`, `ext3_htree_fill_tree`, `ext3_dx_readdir`: Store entries in an rb-tree sorted by hash and deliver them through a `filldir` callback across repeated readdir calls.
- `ext3_dx_find_entry`: Lookup a name in htree leaf blocks, continuing through collision/continuation blocks.
- `ext3_dx_add_entry`, `do_split`, `dx_move_dirents`, `dx_pack_dirents`, `make_indexed_dir`: Insert into indexed directories, split leaves/indexes, and create an index from a one-block directory.
- `ext3_add_entry`: Top-level insertion helper; tries htree insertion, falls back to linear scan on bad indexes, converts eligible one-block directories to htree, or appends a new block.
- `ext3_delete_entry`: Removes a dirent by merging its record length into the previous entry or zeroing the first entry's inode.
- `ext3_is_dir_empty`: Verifies `.` and `..`, then scans for any live entries.
- `ext3_find_entry`, `search_dirblock`: Find a named entry using htree when appropriate and otherwise linearly scans with small readahead.

Important interactions:
- `dirctl.c` calls `ext3_dx_readdir` for htree-backed directory enumeration and falls back to linear scanning on `ERR_BAD_DX_DIR`.
- `generic.c` calls `ext3_add_entry`, `ext3_find_entry`, `ext3_delete_entry`, `ext3_is_dir_empty`, and metadata helpers for create/remove/rename-like operations.
- Block reads use `Ext2MapExtent` or `Ext2MapIndirect`, then `sb_getblk`/`bh_submit_read`.
- Directory growth goes through `Ext2ExpandFile` and updates Windows FCB allocation, file size, and valid data length.

Notable behavior and risks:
- `dx_probe` treats unsupported hash versions, flags, depths over one, bad limits, or bad counts as `ERR_BAD_DX_DIR`; callers must prevent this internal code from surfacing directly to user mode.
- Htree readdir caches entries in `file->private_data`; `ext3_release_dir` frees that state only when htree support is compiled in.
- `ext3_find_entry` disables htree lookup for create IRPs and performs linear search instead.
- Htree insertion can clear `EXT3_INDEX_FL` and continue with linear behavior when the index is corrupt.
- `add_dirent_to_buf` releases the buffer on all outcomes except `-ENOSPC`, so callers must respect that ownership convention.

# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass4.c

This file implements `fsck.gfs2` pass 4, which reconciles inode reference counts after directory traversal. It compares counted links accumulated during earlier passes against on-disk `i_nlink`, repairs mismatches, and handles unlinked inodes by clearing them or moving them into `lost+found`.

The entry point `pass4()` runs three scans:
- `scan_inode_list()` for normal inodes in `cx->inodetree`.
- `scan_dir_list()` for directories in `cx->dirtree`.
- `scan_nlink1_list()` for single-link inodes tracked only in `nlink1map`/`clink1map`.

`handle_unlinked()` covers unreferenced dinodes. If the bitmap says the block is free/bad, it can delete metadata and extended attributes using `pass4_fxns_delete`. If the block is not a dinode, it can clear it. Valid unlinked zero-size inodes can be freed; otherwise the inode can be added to `lost+found`, with link counts adjusted. `handle_inconsist()` fixes mismatched link counts by loading the inode and calling `fix_link_count()`.

Dependencies include `libgfs2`, `link`, `lost_n_found`, `inode_hash`, `metawalk`, `util`, and pass2/pass3 accounting state.

Risks and notes:
- The file mutates metadata trees, eattrs, bitmap state, and link counts; user choices heavily determine outcome.
- `adjust_lf_links()` is needed because adding items to `lost+found` changes its own counted link total.
- `scan_nlink1_list()` linearly scans `0..last_fs_block`, which may be expensive on large filesystems.

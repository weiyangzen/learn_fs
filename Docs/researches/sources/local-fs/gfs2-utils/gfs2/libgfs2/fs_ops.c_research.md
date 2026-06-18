# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/fs_ops.c

This is libgfs2's core inode, block mapping, file I/O, and directory operation implementation.

Major API families:
- Inode lifecycle: `lgfs2_inode_get()`, `lgfs2_inode_read()`, `lgfs2_inode_put()`, `lgfs2_inode_free()`, `lgfs2_is_system_inode()`.
- Allocation: `lgfs2_dinode_alloc()`, `lgfs2_meta_alloc()`, `lgfs2_file_alloc()`, `lgfs2_free_block()`.
- File layout: `lgfs2_space_for_data()`, `lgfs2_calc_tree_height()`, `lgfs2_build_height()`, `lgfs2_find_metapath()`, `lgfs2_lookup_block()`, `lgfs2_block_map()`, `lgfs2_unstuff_dinode()`.
- File I/O: `lgfs2_readi()`, `__lgfs2_writei()`, `lgfs2_write_filemeta()`.
- Directory operations: `lgfs2_init_dinode()`, `lgfs2_createi()`, `lgfs2_dir_add()`, `lgfs2_dir_search()`, `lgfs2_lookupi()`, `lgfs2_dirent_del()`, `lgfs2_dir_split_leaf()`, `lgfs2_get_leaf_ptr()`, `lgfs2_get_leaf()`, `lgfs2_dirent_first()`, `lgfs2_dirent_next()`, `lgfs2_dirent2_del()`.

Important behavior:
- Supports stuffed inodes and unstuffs them when data no longer fits in the dinode body.
- Builds indirect metadata trees on demand for files and journaled-data directories.
- Allocates blocks from resource groups and updates bitmap state, free counts, dinode counts, and superblock accounting.
- Implements linear directories and extended-hash directories.
- Converts stuffed directories to exhash form, doubles hash tables, splits leaves, and chains overflow leaves.
- Initializes new directory dinodes with `.` and `..`.
- `lgfs2_lookupi(".")` returns the input directory inode itself.

Integration role:
- Central implementation behind mkfs, grow, jadd, fsck/edit-like tools, journal construction, metadata language access, and superblock/rindex handling.
- Depends on buffer I/O, bitmap helpers, resource groups, disk hash, and ondisk conversion helpers.

State and ownership:
- `lgfs2_inode_read()` returns an inode owning its buffer head.
- `lgfs2_inode_put()` writes modified in-core dinode fields back into the buffer, releases owned buffers, and frees the inode.
- `lgfs2_inode_free()` discards modifications.
- Directory mutation marks affected inode and leaf buffers modified.

Risk notes:
- This file mutates on-disk metadata directly; allocation, endian conversion, and dirty-buffer handling are high risk.
- Directory splitting and exhash growth contain subtle record-length and entry-count invariants.
- `lgfs2_lookupi(".")` returns an existing inode pointer, so ownership differs from ordinary lookup results.
- `lgfs2_file_alloc()` assumes contiguous extent allocation and is used for mkfs-style construction.
- Error paths can leave partially allocated blocks or directory entries if callers do not recover.

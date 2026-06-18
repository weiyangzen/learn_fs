# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/dirblocks.h

Read coverage: complete file read, 58 lines.

Purpose: declares directory-block tracking and indexed-directory rebuild helpers.

Key API:
- `o2fsck_dirblocks` rb-tree root plus block count.
- `o2fsck_dirblock_entry` fields for owning inode, block number, and block count.
- `o2fsck_add_dir_block()`, `o2fsck_dir_block_iterate()`, reindex-directory lookup/add helpers, `o2fsck_rebuild_indexed_dirs()`, and `o2fsck_check_dir_index()`.

Dependencies: OCFS2 structures and kernel rbtree API.

# File Research: sources/local-fs/ocfs2-tools/libocfs2/unlink.c

Implements directory entry removal for OCFS2 userspace operations, supporting both classic directory blocks and indexed directories.

Key responsibilities:
- Removes a matching directory entry by name and/or inode.
- For classic directories, iterates entries and clears the inode field.
- For indexed directories, updates the data leaf, free-list metadata, dx leaf or inline dx entries, root count, and inode.

Important functions:
- `unlink_proc()`: classic directory iterator callback.
- `ocfs2_unlink_el()`: extent-list directory unlink path.
- `__ocfs2_delete_entry()`: merges a deleted entry into the previous record where possible.
- `ocfs2_unlink_dx()`: indexed-directory unlink path.
- `ocfs2_unlink()`: public API that checks RW mode and dispatches based on directory features.

Dependencies:
- Directory iteration, indexed directory search/write APIs.
- `ocfs2_read_inode`, `ocfs2_read_dx_root`, `ocfs2_dx_dir_search`, `ocfs2_write_dir_block`, `ocfs2_write_dx_leaf`, `ocfs2_write_dx_root`.

Research notes:
- Indexed unlink requires a non-null name and uses dx lookup results.
- The dx path updates `db_free_rec_len` and may add the leaf to the root free-list.
- The classic path reports `OCFS2_ET_DIR_NO_SPACE` when no matching entry was found, inherited from ext2fs-style behavior.

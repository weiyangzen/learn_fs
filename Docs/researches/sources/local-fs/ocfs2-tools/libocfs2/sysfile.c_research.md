# File Research: sources/local-fs/ocfs2-tools/libocfs2/sysfile.c

Small helper for resolving OCFS2 system inode names to inode block numbers.

Key function:
- `ocfs2_lookup_system_inode(fs, type, slot_num, blkno)`

Behavior:
- Allocates a filename buffer sized for `OCFS2_MAX_FILENAME_LEN + 1`.
- Builds the system inode name with `ocfs2_sprintf_system_inode_name()`.
- Looks it up in `fs->fs_sysdir_blkno` using `ocfs2_lookup()`.
- Frees the temporary buffer before returning.

Dependencies:
- `ocfs2_malloc0`, `ocfs2_free`, `ocfs2_sprintf_system_inode_name`, `ocfs2_lookup`.

Research notes:
- This is a central lookup primitive used by slot maps, mkfs finalization, and other system-file operations.
- It assumes `fs->fs_sysdir_blkno` is already known and valid.

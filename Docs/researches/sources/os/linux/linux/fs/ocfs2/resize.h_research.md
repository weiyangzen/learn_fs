# File Research: sources/os/linux/linux/fs/ocfs2/resize.h

`resize.h` is the public header for OCFS2 online resize operations.

Main contents:
- Declares `ocfs2_group_extend(struct inode *inode, int new_clusters)`, which extends the filesystem into unused space at the end of the last existing global bitmap group.
- Declares `ocfs2_group_add(struct inode *inode, struct ocfs2_new_group_input *input)`, which adds a new group descriptor to the global bitmap.

Key invariants:
- The header intentionally exposes only the two resize entry points; validation, backup superblock handling, and bitmap chain updates remain private to `resize.c`.

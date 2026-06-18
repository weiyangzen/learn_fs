# File Research: sources/os/linux/linux-stable/fs/ocfs2/resize.h

Purpose: declares OCFS2 online resize entry points.

Read coverage: complete file read, 16 lines.

Key contents:
- Header guard `OCFS2_RESIZE_H`.
- Declares `ocfs2_group_extend(struct inode *inode, int new_clusters)`.
- Declares `ocfs2_group_add(struct inode *inode, struct ocfs2_new_group_input *input)`.

Dependencies:
- Callers provide an inode from the mounted filesystem; implementations operate on the global bitmap system inode.
- `ocfs2_group_add()` depends on `struct ocfs2_new_group_input` from OCFS2 on-disk/ioctl definitions.

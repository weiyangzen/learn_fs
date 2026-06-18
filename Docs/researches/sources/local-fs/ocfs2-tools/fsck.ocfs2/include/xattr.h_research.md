# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/xattr.h

Read coverage: complete file read, 26 lines.

Purpose: declares extended-attribute validation entry point.

API: `o2fsck_check_xattr(o2fsck_state *ost, struct ocfs2_dinode *di)`.

Role: lets inode scanning validate and repair inode/block/bucket xattr structures.

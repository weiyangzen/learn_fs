# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass1.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 1 and inode allocator cleanup.

API:
- `o2fsck_pass1(o2fsck_state *ost)`
- `o2fsck_free_inode_allocs(o2fsck_state *ost)`

Role: pass 1 walks allocated inodes, validates inode metadata and extent trees, and builds allocation/reference accounting.

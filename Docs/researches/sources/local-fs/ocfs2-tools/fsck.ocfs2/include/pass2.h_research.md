# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass2.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 2 directory-entry checks.

API:
- `o2fsck_pass2(o2fsck_state *ost)`
- `o2fsck_test_inode_allocated(o2fsck_state *ost, uint64_t blkno)`

Role: validates directory entries and records relationship/link metadata for later passes.

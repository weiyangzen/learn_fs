# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass3.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 3 connectivity checks.

API:
- `o2fsck_pass3(o2fsck_state *ost)`
- `o2fsck_reconnect_file(o2fsck_state *ost, uint64_t inode)`

Role: ensures directories are reachable and reconnects orphaned filesystem objects to `lost+found` when needed.

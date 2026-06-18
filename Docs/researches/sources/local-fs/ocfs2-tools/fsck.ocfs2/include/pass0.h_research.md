# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass0.h

Read coverage: complete file read, 32 lines.

Purpose: declares fsck pass 0.

API: `o2fsck_pass0(o2fsck_state *ost)`.

Role: pass 0 validates and repairs chain allocators and group descriptor structures before inode/data passes depend on allocator accounting.

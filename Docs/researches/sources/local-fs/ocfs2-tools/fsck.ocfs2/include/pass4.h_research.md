# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/pass4.h

Read coverage: complete file read, 33 lines.

Purpose: declares fsck pass 4 and orphan-dir replay helper.

API:
- `replay_orphan_dir(o2fsck_state *ost, int slot_recovery)`
- `o2fsck_pass4(o2fsck_state *ost)`

Role: resolves inode link counts, handles disconnected non-directory inodes, and replays orphan directory cleanup.

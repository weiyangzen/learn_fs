# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/slot_recovery.h

Read coverage: complete file read, 30 lines.

Purpose: declares slot recovery helpers run before or after fsck passes.

Key API:
- `o2fsck_replay_truncate_logs()`
- `o2fsck_replay_local_allocs()`
- `o2fsck_replay_orphan_dirs()`

Role: recovers per-slot allocator, truncate-log, and orphan-dir state outside normal pass scanning.

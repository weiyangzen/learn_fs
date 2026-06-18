# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/slot_recovery.c

Purpose: implements slot recovery helpers for fsck, replaying per-slot truncate logs, local alloc windows, and orphan directories before or during full checking.

Read coverage: complete file read, 205 lines.

Key responsibilities:
- Replays truncate logs by verifying all referenced clusters are allocated, freeing them, clearing log records, and writing the truncate log inode.
- Replays local allocs by freeing clear bits still reserved in the global bitmap, then clearing local alloc inode state.
- Replays orphan directories through shared pass 4 orphan replay logic, then resets orphan directory link counts to 2.
- Applies recovery callbacks to each per-slot system file via `handle_slots_system_file()`.

Important entry points:
- `o2fsck_replay_truncate_logs()`
- `o2fsck_replay_local_allocs()`
- `o2fsck_replay_orphan_dirs()`
- Internal callbacks: `ocfs2_clear_truncate_log()`, `ocfs2_clear_local_alloc()`, and `ocfs2_clear_link_count()`.

Dependencies:
- Uses libocfs2 cluster test/free, inode write, local alloc sizing, truncate-log sizing, and per-slot system inode lookup through `util.c`.
- Calls `replay_orphan_dir()` from `pass4.c`.

Risk and edge cases:
- Each recovery callback validates expected system inode flags and returns invalid-argument/internal errors on unexpected metadata.
- Local alloc replay verifies clusters are still allocated before freeing; missing bits become `OCFS2_ET_INVALID_BIT`.
- Orphan directory replay returns errors during slot recovery to trigger broader fsck handling.

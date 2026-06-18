# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/journal.h

Read coverage: complete file read, 36 lines.

Purpose: declares fsck journal checking, replay, and cleanup APIs.

Key API:
- `o2fsck_replay_journals()`
- `o2fsck_should_replay_journals()`
- `o2fsck_clear_journal_flags()`
- `o2fsck_check_journals()`

Dependencies: `fsck.h` and libocfs2 journal structures.

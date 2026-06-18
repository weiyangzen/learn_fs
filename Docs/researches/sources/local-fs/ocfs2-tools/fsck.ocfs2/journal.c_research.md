# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/journal.c

Read coverage: complete file read, 1138 lines.

Purpose: checks, replays, repairs, and clears OCFS2 per-slot JBD2 journal state for fsck.

Major behavior:
- Maintains `journal_info` per slot: slot number, replay flag, journal inode/cached inode, journal superblock and block, revoke rb-tree, final sequence, and shared duplicate-block bitmap.
- `o2fsck_should_replay_journals()` scans all journal inodes for `OCFS2_JOURNAL_DIRTY_FL`, reads journal superblocks, and decides whether any `s_start` requires replay.
- `o2fsck_replay_journals()` performs a first scan of each dirty journal to validate tags, detect duplicate journal block mappings, build revoke records, and determine final sequence; then performs recovery scans that write journaled blocks to target disk blocks unless revoked.
- Replay resets `s_start` and advances `s_sequence`, but intentionally leaves the dirty flag until orphan-dir handling can be completed.
- Journal walking understands descriptor, commit, and revoke blocks, JBD2 sequence wrap comparisons, tag sizes, `JBD2_FLAG_LAST_TAG`, `JBD2_FLAG_SAME_UUID`, and escaped magic restoration.
- `o2fsck_check_journals()` validates all journal files before normal fsck: reads journal superblocks, records feature sets and sizes, finds a good reference journal or consistent known problem, and prompts to regenerate/extend/reset journals when possible.
- `o2fsck_clear_journal_flags()` clears OCFS2 dirty flags and clears any JBD2 superblock `s_errno`.

Important dependencies:
- JBD2 on-disk headers, tags, commit/revoke semantics.
- OCFS2 system inode lookup, cached inode extent mapping, journal superblock read/write helpers, block bitmap APIs, and raw block I/O.
- Prompt codes for invalid journals, unknown/missing features, too-small journals, and dirty flag cleanup.
- `handle_slots_system_file()` for applying cleanup to all slot journal inodes.

Risk notes:
- The file intentionally ignores journals with consistency problems rather than replaying unsafe data.
- I/O errors during replay can cause partial replay, following kernel JBD2 expectations, and fsck warns the user.
- Revoke handling is present but comments note it was historically untested.
- If every journal has unsupported features, fsck refuses and tells the user to upgrade instead of rewriting unknown-format journals.

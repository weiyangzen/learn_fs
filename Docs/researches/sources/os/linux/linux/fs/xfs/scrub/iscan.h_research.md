# File Research: sources/os/linux/linux/fs/xfs/scrub/iscan.h

Defines the live inode scan state and public API.

Key fields in `struct xchk_iscan`:
- `scan_start_ino`, `cursor_ino`, and `__visited_ino` define scan progress and wraparound.
- `skip_ino` excludes a specific inode from scanning.
- `__opstate` stores abort and trylock-AGI flags.
- `iget_timeout`, `iget_retry_delay`, and `__iget_deadline` control inode acquisition retries.
- `__batch_ino`, `__skipped_inomask`, and `__inodes[]` support chunk-sized batching and live updates for skipped inodes.

Public API:
- Start/finish/teardown: `xchk_iscan_start`, `xchk_iscan_finish_early`, `xchk_iscan_teardown`.
- Iteration: `xchk_iscan_iter`, `xchk_iscan_iter_finish`.
- Progress/update helpers: `xchk_iscan_mark_visited`, `xchk_iscan_want_live_update`.
- Inline state helpers: abort and trylock-AGI accessors.

This header is central to scrub tasks that build replacement metadata while the filesystem remains live.

# File Research: sources/local-fs/jfsutils/libfs/logredo.c

This file orchestrates JFS journal replay. It owns global replay state, detects inline versus external logs, validates log and filesystem superblocks, scans the log backward, dispatches record handling to `log_work.c`, flushes recovered pages, updates maps and superblocks, and finalizes the journal.

Major global state:
- `logsup`, `Log`, `vopen[MAX_ACTIVE]`, and `primary_vol`.
- File page buffer cache: `bufhdr[NBUFPOOL]` plus `buffer[]`.
- Log data buffer `afterdata[LOGPSIZE * 2]`.
- Memory fallback state used when bmap workspace allocation fails.
- `use_2ndary_agg_superblock`, `retcode`, and `end_of_transaction`.

Main functions:
- `jfs_logredo()` is the public replay entry point.
- `doMount()` marks a dirty/logredo volume clean when a mount record is reached.
- `openVol()` opens and validates a filesystem associated with a log, checks clean state and log serial, initializes map workspaces, and validates inline-log sizing.
- `updateSuper()` rewrites the filesystem superblock state after replay.
- `rdwrSuper()` reads or writes primary/secondary aggregate superblocks with endian conversion.
- `bflush()` writes modified page-cache buffers to their described PXD extent length.
- `findLog()` classifies the supplied file as a filesystem with inline log, filesystem with external log, or external log device.
- `fsError()` and `logError()` centralize diagnostic messages and mark affected volumes/log state as needing fsck/logredo attention.
- `recoverExtendFS()` repairs crashes during inline-log `extendfs()`, choosing pre-extend or post-extend recovery based on bmap size state.
- `alloc_dmap_bitrec()` and `alloc_storage()` allocate workspace through fsck and optionally reuse bmap storage if normal allocation fails.
- Debug-only helpers provide hex dumps and log descriptor printing.

Replay flow:
1. `findLog()` validates the target and detects whether the log is inline or external.
2. Inline `FM_EXTENDFS` volumes divert into `recoverExtendFS()`.
3. The log superblock is read, swapped, validated, and checked for in-use external logs.
4. Already-redone logs return quickly, updating inline filesystem superblock if needed.
5. `findEndOfLog()` locates the replay start.
6. `logredoInit()` allocates runtime tables and opens affected volumes.
7. Records are read backward with `logRead()` until the sync point target is reached.
8. Record dispatch handles commit, mount, sync point, redopage, noredopage, noredoinoext, and updatemap records.
9. Buffers flush at transaction boundaries and at the end.
10. Extended dtree-page freelists are rebuilt.
11. Allocation maps and superblocks are updated for open volumes.
12. The log active list is cleared and the log superblock is marked `LOGREDONE`.

Integration points:
- `log_read.c` supplies `findEndOfLog()` and `logRead()`.
- `log_work.c` supplies `logredoInit()`, record handlers, and map/page update primitives.
- `logform.c` is used by extendfs recovery.
- `open_by_label.c` is used to locate external logs and active filesystems by UUID.
- `fsck_message.h` supplies detailed diagnostics.

Risks and notes:
- `findLog()` contains a suspicious inline-log test in `openVol()`: `(sb.s_flag & (JFS_INLINELOG == JFS_INLINELOG))` effectively masks with `1`, not `JFS_INLINELOG`; this works only if `JFS_INLINELOG` is bit 0.
- `alloc_storage()` uses `Insuff_memory_for_maps & (available_stg_bytes != 0)` instead of logical `&&`; because the operands are integer flags, it behaves as intended for current values but is brittle.
- External log open handling relies on `O_EXCL` without `O_CREAT`; this is used as an advisory exclusivity signal through `fopen_excl()`, not a POSIX lock.

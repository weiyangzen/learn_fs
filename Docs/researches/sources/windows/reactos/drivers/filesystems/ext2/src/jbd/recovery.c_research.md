# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/jbd/recovery.c

## Scope
Provides Linux JBD journal recovery logic used by the ReactOS Ext2 driver. It scans the journal, records revoke entries, replays committed descriptor data, and supports skip-recovery startup.

## Key Elements
- `journal_recover()` performs the classic three recovery passes: `PASS_SCAN`, `PASS_REVOKE`, and `PASS_REPLAY`.
- `journal_skip_recovery()` scans enough journal state to advance transaction sequence numbers while ignoring existing log contents.
- `do_one_pass()` walks the circular journal, validates magic, block type, and transaction sequence, handles descriptor, commit, and revoke blocks, wraps at journal bounds, and records end transaction state.
- `jread()` maps journal offsets with `journal_bmap()`, gets a buffer head, performs readahead where enabled, waits for data, and returns IO errors on failed reads.
- `count_tags()` counts descriptor tags, accounting for optional UUID fields and `JFS_FLAG_LAST_TAG`.
- `scan_revoke_records()` parses revoke blocks and calls `journal_set_revoke()` for each revoked block.

## Dependencies
Depends on JBD journal structures, `journal_bmap()`, buffer-head IO helpers supplied by the Linux shim, revoke APIs from `revoke.c`, transaction ID comparison helpers, endian conversion macros, and block-device sync.

## Behavior/Risks
- Replay copies logged data blocks back to filesystem-device blocks unless `journal_test_revoke()` suppresses them.
- IO errors during replay attempt to recover what they can but return failure after the pass.
- Recovery trusts descriptor tag bounds and revoke block `r_count`; malformed journal metadata is handled mostly by stopping scan or returning IO-style errors.
- At the end of successful recovery, the transaction sequence advances past the recovered range and revoke state is cleared.

# sources/test-tools/xfstests/tests/generic/479

## Purpose
Test that when a fsync journal/log exists, if we rename a special file (fifo, symbolic link or device), create a hard link for it with its old name and then commit the journal/log, if a power loss happens the filesystem will not fail to replay the journal/log when it is mounted the next time. It is registered as generic/479 with `_begin_fstest` tags `auto, quick, metadata, log`, making it part of the crash recovery/log replay, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, run_test. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, rename/link persistence. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem; forces filesystem writeback/transaction commit; requires a journal/log capable filesystem before crash replay; routes the scratch device through dm-flakey; simulates power loss and remounts for replay.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; remounts or replays after simulated failure; wraps repeated scenarios in local helper functions _cleanup, run_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmflakey, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_symlinks; _require_mknod; _require_dm_target flakey; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, ln, mkdir, mkfifo, mknod, mv, rm, touch.

Representative `xfs_io` operations: fsync.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

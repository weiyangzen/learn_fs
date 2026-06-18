# sources/test-tools/xfstests/tests/generic/464

## Purpose
Run delalloc writes & append writes & non-data-integrity syncs concurrently to test the race between block map change vs writeback. It is registered as generic/464 with `_begin_fstest` tags `auto, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: getfile, do_write, do_append, do_writeback. Important state variables and paths include MAXFILES=200, BLOCK_SZ=65536, LOOP_CNT=10, LOOP_TIME=5, PROC_CNT=16, stop=$tmp.stop. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions getfile, do_write, do_append, do_writeback.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_xfs_io_command "sync_range".

External/helper commands: $XFS_IO_PROG, rm, touch.

Representative `xfs_io` operations: sync_range -w 0 0.

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

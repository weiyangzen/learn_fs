# sources/test-tools/xfstests/tests/generic/427

## Purpose
Try to trigger a race of free eofblocks and file extending dio writes. A known bug of XFS has been fixed by "e4229d6 xfs: fix eofblocks race with file extending async dio writes". It is registered as generic/427 with `_begin_fstest` tags `auto, quick, aio, rw`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include open_close_pid=$!, nr_cpu=`$here/src/feature -o`, fsize=$((nr_cpu * 10)). Topic focus: general filesystem semantics. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_test_program "feature"; _require_aiodio aio-dio-eof-race; _require_no_compress; _require_inplace_writes $SCRATCH_MNT.

External/helper commands: $XFS_IO_PROG, rm.

Representative `xfs_io` operations: pwrite -S 0x55 0 $((256 * 1024 * 1024 * 2)).

## Risks and Edge Cases
timing and workload races can expose intermittent kernel behavior.

## Test Signals
The golden `.out` expects normalized signals such as: Success, all done.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

# sources/test-tools/xfstests/tests/generic/402

## Purpose
Test to verify filesystem timestamps for supported ranges. Exit status 1: test failed. Exit status 0: test passed. It is registered as generic/402 with `_begin_fstest` tags `auto, quick, rw, bigtime`, making it part of the filesystem regression behavior coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: check_stat, run_test_individual, run_test. Important state variables and paths include update_time=1, n=1, update_time=0. Topic focus: general filesystem semantics. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure; checks visible metadata, extent maps, hashes, or syscall output; wraps repeated scenarios in local helper functions check_stat, run_test_individual, run_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_check_dmesg; _require_xfs_io_command utimes; _require_timestamp_range $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, attr, grep, rm, stat.

Representative `xfs_io` operations: utimes $timestamp 0 $timestamp 0.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

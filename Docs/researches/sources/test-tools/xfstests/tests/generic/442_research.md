# sources/test-tools/xfstests/tests/generic/442

## Purpose
Test writeback error handling when writing to block devices via pagecache. See src/fsync-err.c for details of what test actually does. It is registered as generic/442 with `_begin_fstest` tags `blockdev, eio`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: writeback error reporting. Key helper behavior includes: formats a fresh scratch filesystem; sets up dm-error for I/O fault injection.

## Control Flow
formats the scratch filesystem; initializes device-mapper or log-writes infrastructure; forces durability boundaries with sync/fsync operations; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses sync-family calls as persistence barriers.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target error; _require_test_program fsync-err; _require_test_program dmerror.

External/helper commands: rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Test passed!. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

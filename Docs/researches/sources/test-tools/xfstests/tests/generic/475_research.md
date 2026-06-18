# sources/test-tools/xfstests/tests/generic/475

## Purpose
Test log recovery with repeated (simulated) disk failures. We kick off fsstress on the scratch fs, then switch out the underlying device with dm-error to see what happens when the disk goes down. Having taken down the fs in this manner, remount it and repeat. This test is a Good Enough (tm) simulation of our internal multipath failure testing efforts. It is registered as generic/475 with `_begin_fstest` tags `shutdown, auto, log, metadata, eio, recoveryloop, smoketest`, making it part of the crash recovery/log replay, writeback error reporting, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, writeback error reporting, fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; requires a journal/log capable filesystem before crash replay; sets up dm-error for I/O fault injection; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; initializes device-mapper or log-writes infrastructure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/dmerror, common/preamble.

Prerequisite gates: _require_scratch; _require_dm_target error; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: mount, rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures; writeback error propagation is asynchronous and must be checked at the intended boundary.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

# sources/test-tools/xfstests/tests/generic/388

## Purpose
Test XFS log recovery ordering on v5 superblock filesystems. XFS had a problem where it would incorrectly replay older modifications from the log over more recent versions of metadata due to failure to update metadata LSNs during log recovery. This could result in false positive reports of corruption during log recovery and permanent mount failure. To test this situation, run frequent shutdowns immediately after log recovery. Ensure that log recovery does not recover stale modifications and cause spurious corruption reports and/or mount failures. It is registered as generic/388 with `_begin_fstest` tags `shutdown, auto, log, metadata, recoveryloop`, making it part of the crash recovery/log replay, fsstress/replay consistency coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: crash recovery/log replay, fsstress/replay consistency. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem; forces unmount/remount persistence checks; requires a journal/log capable filesystem before crash replay; starts fsstress workload generation.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; remounts or replays after simulated failure.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/preamble.

Prerequisite gates: _require_scratch; _require_local_device $SCRATCH_DEV; _require_scratch_shutdown; _require_metadata_journaling $SCRATCH_DEV.

External/helper commands: mount.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden.. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

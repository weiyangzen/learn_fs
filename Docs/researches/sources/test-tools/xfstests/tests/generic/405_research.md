# sources/test-tools/xfstests/tests/generic/405

## Purpose
Test mkfs against thin provision device, which has very small backing size, mkfs should return error when it hits EIO. It is registered as generic/405 with `_begin_fstest` tags `auto, mkfs, thin`, making it part of the writeback error reporting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include BACKING_SIZE=$((1 * 1024 * 1024 / 512)), VIRTUAL_SIZE=$((1 * 1024 * 1024 * 1024 * 1024 / 512)). Topic focus: writeback error reporting. Key helper behavior includes: sets up dm-thin backing storage.

## Control Flow
initializes device-mapper or log-writes infrastructure; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
explicitly validates behavior across remount, crash replay, or log replay.

## Dependencies and Integration Points
Common libraries: common/dmthin, common/filter, common/preamble.

Prerequisite gates: _require_scratch_nocheck; _require_dm_target thin-pool.

External/helper commands: rm.

## Risks and Edge Cases
device-mapper setup, replay ordering, or host capabilities can dominate failures.

## Test Signals
The golden `.out` expects normalized signals such as: Silence is golden. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

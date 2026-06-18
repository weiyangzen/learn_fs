# sources/test-tools/xfstests/tests/generic/381

## Purpose
Test xfs_quota when user or names beginning with digits. For example, create a 'limit' for a user or group named '12345678-abcd', then query this user and group. It is registered as generic/381 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: quota accounting. Key helper behavior includes: formats a fresh scratch filesystem.

## Control Flow
formats the scratch filesystem.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_user 123456-fsgqa; _require_group 123456-fsgqa.

External/helper commands: grep.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: == user test ==; === quota command output ===; SCRATCH_DEV 0 102400 204800 00 [--------] SCRATCH_MNT; === report command output ===; 123456-fsgqa 0 102400 204800 00 [--------]; == group test ==. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

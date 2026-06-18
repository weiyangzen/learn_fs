# sources/test-tools/xfstests/tests/generic/383

## Purpose
Test xfs_quota when project names beginning with digits. It is registered as generic/383 with `_begin_fstest` tags `auto, quick, quota`, making it part of the quota accounting, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: do_project_test. Important state variables and paths include qa_user=. Topic focus: quota accounting, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions do_project_test.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_prjquota $SCRATCH_DEV.

External/helper commands: mkdir.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: === quota command output ===; Disk quotas for Project 123456-project (10); Filesystem Files Quota Limit Warn/Time Mounted on; SCRATCH_DEV 1 100 200 00 [--------] SCRATCH_MNT; === report command output ===; 123456-project 1 100 200 00 [--------]. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

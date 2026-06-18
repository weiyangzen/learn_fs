# sources/test-tools/xfstests/tests/generic/385

## Purpose
Make sure renames accross project boundaries are properly rejected and that we don't use the wrong lock flags internally. Based on a report and testcase from Arkadiusz Miskiewicz <arekm@maven.pl>. It is registered as generic/385 with `_begin_fstest` tags `quota, auto, quick`, making it part of the rename/link persistence, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup. Important state variables and paths include quota_cmd=$XFS_QUOTA_PROG -D $tmp.projects -P $tmp.projid. Topic focus: rename/link persistence, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions _cleanup.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign; _require_prjquota $SCRATCH_DEV.

External/helper commands: mkdir, rm, touch.

## Risks and Edge Cases
failures may reflect missing helper binaries or unsupported filesystem features rather than the target regression.

## Test Signals
The golden `.out` expects normalized signals such as: rename: No such file or directory; rename: No such file or directory; rename: No such file or directory; rename: No such file or directory; rename: No such file or directory; rename: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

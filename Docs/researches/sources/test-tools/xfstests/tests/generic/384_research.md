# sources/test-tools/xfstests/tests/generic/384

## Purpose
test to reproduce PV951636: project quotas not updated if a file is mv'd into that directory. It is registered as generic/384 with `_begin_fstest` tags `quota, auto, quick`, making it part of the ACL/permission semantics, rename/link persistence, quota accounting, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, report_quota. Important state variables and paths include dir=$SCRATCH_MNT/project. Topic focus: ACL/permission semantics, rename/link persistence, quota accounting, filename/directory semantics. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; creates deterministic file layout, data, or extent state; wraps repeated scenarios in local helper functions _cleanup, report_quota.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_test; _require_quota; _require_xfs_quota_foreign; _require_xfs_io_command "chproj"; _require_scratch; _require_prjquota $SCRATCH_DEV.

External/helper commands: $XFS_IO_PROG, chmod, cp, mkdir, mv, rm, touch.

Representative `xfs_io` operations: chproj -R 1; chattr -R +P; limit -p bsoft=100m bhard=100m 1.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: #1 1 0 0 00 [--------]; #1 4 0 0 00 [--------]; #1 5 0 0 00 [--------]; #1 6 0 0 00 [--------]. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

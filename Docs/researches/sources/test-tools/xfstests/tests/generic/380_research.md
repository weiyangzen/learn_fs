# sources/test-tools/xfstests/tests/generic/380

## Purpose
To test out pv#940675 crash in xfs_trans_brelse + quotas Without the fix, this will create an ASSERT failure in debug kernels and crash a non-debug kernel. It is registered as generic/380 with `_begin_fstest` tags `quota, auto, quick`, making it part of the ACL/permission semantics, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _chowning_file. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: ACL/permission semantics, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; wraps repeated scenarios in local helper functions _chowning_file.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign.

External/helper commands: chown, ls, mount, sed, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: mkfs on scratch; mount with quotas; creating quota file with holes; ..........; now fill in the holes; .................................................................................................................................................................................................................................................................. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

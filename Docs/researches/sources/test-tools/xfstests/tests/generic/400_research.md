# sources/test-tools/xfstests/tests/generic/400

## Purpose
test out high quota ids retrieved by Q_GETNEXTQUOTA Request for next ID near 2^32 should not wrap to 0 Designed to use the new Q_GETNEXTQUOTA quotactl. It is registered as generic/400 with `_begin_fstest` tags `auto, quick, quota`, making it part of the ACL/permission semantics, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include MOUNT_OPTIONS=-o usrquota,grpquota, ID=4294967292. Topic focus: ACL/permission semantics, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_quota; _require_scratch; _require_getnextquota.

External/helper commands: chown, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: Launch all quotas; Ask for ID after 4294967293 expecting nothing; Q_GETNEXTQUOTA: No such file or directory; Q_XGETNEXTQUOTA: No such file or directory; Ask for ID after 4294967293 expecting nothing; Q_GETNEXTQUOTA: No such file or directory. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

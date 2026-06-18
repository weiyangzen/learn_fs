# sources/test-tools/xfstests/tests/generic/379

## Purpose
Check behavior of chown with both user and group quota enabled, and changing both user and group together via chown(2). It is registered as generic/379 with `_begin_fstest` tags `quota, auto, quick`, making it part of the ACL/permission semantics, quota accounting coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: _cleanup, _filter_stat, _exercise. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: ACL/permission semantics, quota accounting. Key helper behavior includes: formats a fresh scratch filesystem; unmounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; wraps repeated scenarios in local helper functions _cleanup, _filter_stat, _exercise.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble, common/quota.

Prerequisite gates: _require_scratch; _require_quota; _require_xfs_quota_foreign.

External/helper commands: chmod, chown, cp, mount, rm, sed, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: *** Default mount options;  File: "<MOUNT>/testfile";  Size: 0 Filetype: Regular File;  Mode: (0644/-rw-r--r--) Uid: (12345) Gid: (54321); Device: <DEVICE> Inode: <INODE> Links: 1;  File: "<MOUNT>/testfile". Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

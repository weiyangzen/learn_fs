# sources/test-tools/xfstests/tests/generic/378

## Purpose
Simple permission check on hard links. Overlayfs had a bug that hardlinks don't share inode, if chmod/chown/etc. is performed on one of the links then the inode belonging to the other one won't be updated. The following patch fixed this issue 51f7e52 ovl: share inode for hard link. It is registered as generic/378 with `_begin_fstest` tags `auto, quick, metadata`, making it part of the ACL/permission semantics, rename/link persistence coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testfile=$TEST_DIR/testfile.$seq, testlink=$testfile.hardlink. Topic focus: ACL/permission semantics, rename/link persistence. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/filter, common/preamble.

Prerequisite gates: _require_test; _require_user; _require_hardlinks.

External/helper commands: chmod, ln, rm.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: Permission denied; Permission denied. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

# sources/test-tools/xfstests/tests/generic/375

## Purpose
Check if SGID is cleared upon chmod / setfacl when the owner is not in the owning group. It is registered as generic/375 with `_begin_fstest` tags `auto, quick, acl, perms`, making it part of the ACL/permission semantics, filename/directory semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include no persistent shell variables beyond harness state. Topic focus: ACL/permission semantics, filename/directory semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_runas; _require_acls.

External/helper commands: attr, chmod, chown, mkdir, rm, setfacl, stat, touch.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: *** SGID should remain set (twice); -rwxrwsrwx; -rwxrwsrwx; *** SGID should be cleared (twice); -rwxrwxrwx; -rwxrwxrwx. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

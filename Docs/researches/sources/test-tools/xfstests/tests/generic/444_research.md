# sources/test-tools/xfstests/tests/generic/444

## Purpose
Check if SGID is inherited when creating a subdirectory when the owner is not in the owning group and directory has default ACLs. It is registered as generic/444 with `_begin_fstest` tags `auto, quick, acl, perms`, making it part of the ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include TDIR=testdir.$seq. Topic focus: ACL/permission semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_runas; _require_acls.

External/helper commands: attr, chmod, chown, mkdir, rm, setfacl, stat.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: drwxrwsr-x; drwxrwsr-x. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

# sources/test-tools/xfstests/tests/generic/449

## Purpose
Fill the device and set as many extended attributes to a file as possible. Then call setfacl on it and, if this fails for lack of space, test that the permissions remain the same. It is registered as generic/449 with `_begin_fstest` tags `auto, quick, acl, attr, enospc`, making it part of the ACL/permission semantics, ENOSPC/free-space handling coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include TFILE=$SCRATCH_MNT/testfile.$seq, i=1, j=1, ret=0. Topic focus: ACL/permission semantics, ENOSPC/free-space handling. Key helper behavior includes: formats a scratch filesystem with a controlled size; formats a fresh scratch filesystem; mounts the scratch filesystem.

## Control Flow
formats the scratch filesystem; mounts the target through the relevant helper layer; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
mutates a freshly formatted scratch filesystem; uses persistent files under TEST_DIR; persists extended-attribute namespace/value state; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_scratch; _require_test; _require_acls; _require_attrs trusted.

External/helper commands: $ATTR_PROG, $SETFATTR_PROG, $XFS_IO_PROG, attr, chmod, mount, setfacl, stat, touch.

Representative `xfs_io` operations: pwrite 0 256m.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: -rwx------. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

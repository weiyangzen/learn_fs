# sources/test-tools/xfstests/tests/generic/389

## Purpose
Test if O_TMPFILE files inherit POSIX Default ACLs when they are linked into the namespace. It is registered as generic/389 with `_begin_fstest` tags `auto, quick, acl`, making it part of the ACL/permission semantics coverage surface.

## Important APIs, Types, and Functions
This is a bash xfstests case, so its API surface is the harness contract rather than exported program symbols. Local functions: none. Important state variables and paths include testdir=${TEST_DIR}/d.$seq, testfile=${testdir}/tst-tmpfile-flink. Topic focus: ACL/permission semantics. The script is mostly linear and relies on xfstests common helpers for setup, filtering, and cleanup.

## Control Flow
operates in the configured test filesystem; creates deterministic file layout, data, or extent state; checks visible metadata, extent maps, hashes, or syscall output.

## State and Persistence Behavior
uses persistent files under TEST_DIR; observes inode mode, ownership, ACL, and permission state.

## Dependencies and Integration Points
Common libraries: common/attr, common/filter, common/preamble.

Prerequisite gates: _require_test; _require_xfs_io_command "-T"; _require_xfs_io_command "flink"; _require_acls.

External/helper commands: $XFS_IO_PROG, attr, mkdir, rm, setfacl, stat.

Representative `xfs_io` operations: pwrite 0 4096; pread 0 4096; flink ${testfile}; %a.

## Risks and Edge Cases
depends on user/group identity setup and permission model details.

## Test Signals
The golden `.out` expects normalized signals such as: wrote 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); read 4096/4096 bytes at offset 0; XXX Bytes, X ops; XX:XX:XX.X (XXX YYY/sec and XXX ops/sec); 664. Extra diagnostics are written to `$seqres.full`. Skips are expected when `_require_*` gates reject the host; failures should be diagnosed from normalized stdout plus `$seqres.full`.

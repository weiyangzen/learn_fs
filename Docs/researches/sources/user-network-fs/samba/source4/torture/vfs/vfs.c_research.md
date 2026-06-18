<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/vfs.c -->
# sources/user-network-fs/samba/source4/torture/vfs/vfs.c

## Purpose

This file is the VFS torture module entry point. It registers VFS-related SMB torture suites, including fruit, acl_xattr, and streams_xattr, and provides a helper for tests that need two SMB2 tree connections to separate shares/namespaces.

## Important APIs, Types, and Functions

- `wrap_2ns_smb2_test()` opens the default SMB2 tree and a second tree from torture option `share2`, runs a two-tree test function, and frees connection state safely.
- `torture_suite_add_2ns_smb2_test()` constructs a `torture_test` that uses `wrap_2ns_smb2_test()`.
- `torture_vfs_init()` creates the top-level `vfs` suite and attaches all VFS sub-suites.

## Control Flow

Two-namespace tests are registered as a tcase with a custom wrapper. At runtime the wrapper opens the first tree with `torture_smb2_connection()`, steals it to a local talloc context so tests that close connections do not cause double-free, optionally opens the second tree via `torture_smb2_con_sopt()`, invokes the stored function pointer, and frees the wrapper context. Module initialization creates the `vfs` suite, adds child suites, adds the standalone fruit AFP info validator, registers the suite, and returns `NT_STATUS_OK`.

## State and Persistence Behavior

This file itself persists no data. It manages SMB2 connection lifetimes through talloc ownership and deliberately tolerates tests that close their own connections. Persistent state is created only by child tests.

## Dependencies and Integration Points

It integrates with the Samba torture framework, SMB2 helper layer, VFS suite constructors from `torture/vfs/proto.h`, and the module system through `torture_vfs_init()`. `torture/wscript_build` compiles it into the `TORTURE_VFS` smbtorture module.

## Risks and Edge Cases

`wrap_2ns_smb2_test()` proceeds even if the second tree open fails; individual two-tree tests must handle a NULL or unusable `tree2`. The manual `struct torture_test` allocation must keep fields in sync with torture framework expectations.

## Test Signals

The main signal is suite availability: VFS subtests appear under `vfs` and run with expected SMB2 connection setup. Failures usually surface as missing VFS tests, failed tree setup, or lifetime bugs when tests close connections themselves.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/vfs/vfs.c -->

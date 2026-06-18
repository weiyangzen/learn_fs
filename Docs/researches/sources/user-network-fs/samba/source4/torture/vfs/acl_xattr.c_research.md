# sources/user-network-fs/samba/source4/torture/vfs/acl_xattr.c

## Purpose

This file defines the `acl_xattr` VFS torture suite. It is a focused SMB2 regression test for `vfs_acl_xattr` behavior when the share is configured to ignore the underlying system ACL and synthesize default ACLs in either POSIX-style or Windows-style mode.

The suite creates a directory, replaces its DACL with a non-inheritable owner-only ACE, creates a child file, reads the child's security descriptor, and checks that the resulting descriptor matches the configured default ACL style. It validates Samba's security descriptor persistence and defaulting behavior as observed over SMB2 rather than testing the VFS module internally.

## Important APIs, Types, and Functions

- `BASEDIR` is the fixed test root `smb2-testsd`.
- `CHECK_SECURITY_DESCRIPTOR(_sd1, _sd2)` compares descriptors with `security_descriptor_equal()`, prints both descriptors with `NDR_PRINT_DEBUG(security_descriptor, ...)` on mismatch, records `TORTURE_FAIL`, and flips the local `ret` flag.
- `test_default_acl_posix()` connects to share `acl_xattr_ign_sysacl_posix` and expects a child file default descriptor containing owner full control, owning group generic read/write/execute, world generic read/write/execute, and system full control.
- `test_default_acl_win()` connects to share `acl_xattr_ign_sysacl_windows` and expects a child file default descriptor containing only owner full control and system full control.
- `torture_acl_xattr()` builds the suite and registers `default-acl-style-posix` and `default-acl-style-windows` as SMB2 tests through `torture_suite_add_1smb2_test()`.

The file uses `struct smb2_tree`, `struct smb2_handle`, `union smb_fileinfo`, `union smb_setfileinfo`, and `struct security_descriptor` as its main protocol-facing types.

## Control Flow

Both test functions share the same structure. They ignore the incoming `tree_unused` parameter and explicitly connect to the share variant under test with `torture_smb2_con_share()`. They call `smb2_util_setup_dir()` to recreate `BASEDIR`, open `BASEDIR\testdir` with `torture_smb2_testdir()`, and query the directory security descriptor using `RAW_FILEINFO_SEC_DESC` with `SECINFO_DACL | SECINFO_OWNER | SECINFO_GROUP`.

The owner and group SIDs from the original directory descriptor are converted to strings with `dom_sid_string()`. The test then builds a new security descriptor with `security_descriptor_dacl_create()` containing one non-inheritable `SEC_ACE_TYPE_ACCESS_ALLOWED` ACE for the owner SID with `SEC_RIGHTS_DIR_ALL`. That descriptor is written back to the directory with `RAW_SFILEINFO_SEC_DESC` and `SECINFO_DACL`.

After closing the directory handle, the test creates `BASEDIR\testdir\testfile` with `torture_smb2_testfile()`, queries the file security descriptor with owner, group, and DACL information, closes the file handle, and constructs the expected descriptor. The POSIX test includes owner, group, world, and system ACEs. The Windows test includes only owner and system ACEs. `CHECK_SECURITY_DESCRIPTOR()` performs the final comparison.

Both tests jump to a common `done:` block on assertion failure. The cleanup block closes any non-empty file or directory handle, deletes `BASEDIR` with `smb2_deltree()`, disconnects the tree with `smb2_tdis()`, and returns the accumulated boolean result.

## State and Persistence Behavior

The test mutates only the configured SMB share. It creates and deletes the fixed tree `smb2-testsd`, creates `testdir` and `testfile`, and writes a DACL onto the directory. Successful cleanup removes the test root at the end of each test. If the process crashes or the server disconnects before `done:`, stale test paths or ACL xattrs can remain on the share.

There is no local file persistence. All security descriptors are talloc-owned under the torture context. The queried owner and group SID strings are derived from the live server response so the expected descriptor is anchored to the actual share identity rather than hard-coded domain SIDs.

## Dependencies and Integration Points

The suite depends on the SMB2 torture utilities, SMB2 getinfo/setinfo calls, security descriptor construction/comparison helpers, generated NDR security printing, Samba loadparm/cmdline plumbing, and the VFS torture registration header. It requires test environment shares named `acl_xattr_ign_sysacl_posix` and `acl_xattr_ign_sysacl_windows`, with configurations that exercise `vfs_acl_xattr` and differ in default ACL style.

Integration is through the global torture registry: `torture_acl_xattr()` creates a suite named `acl_xattr` with description `vfs_acl_xattr tests`. At runtime the tests validate behavior across SMB2, the VFS ACL xattr module, the underlying filesystem ACL/xattr storage, and Samba's NT security descriptor mapping.

## Risks and Edge Cases

The expected descriptors are exact. ACE order, owner/group preservation, generic rights expansion, and default ACL synthesis must match precisely. Any legitimate implementation change that preserves effective access but changes descriptor shape can fail the test.

The test relies on fixed share names. If those shares are absent or not configured with the intended `acl_xattr` options, the test fails at connection setup or reports misleading descriptor differences. Because the initial directory owner and group are captured dynamically, failures usually point to DACL construction/defaulting rather than domain-specific SID values.

The `CHECK_SECURITY_DESCRIPTOR` macro assumes local variables named `tctx` and `ret`, so it is tightly coupled to the test function shape. The tests close handles before comparing descriptors, which is fine for the current flow but can make later debugging slightly less direct if a mismatch depends on live handle state.

## Test Signals

The primary pass signal is an exact `security_descriptor_equal()` match for each share's expected child-file descriptor. Secondary signals include successful setup of `BASEDIR`, successful directory and file creation, successful SMB2 security descriptor query and set calls, and clean deletion of the test tree. Failures indicate regressions in ignored-system-ACL behavior, default ACL style selection, descriptor inheritance/defaulting, SMB2 security descriptor get/set handling, or test share configuration.

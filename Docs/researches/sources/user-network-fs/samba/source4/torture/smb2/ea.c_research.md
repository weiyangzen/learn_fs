# sources/user-network-fs/samba/source4/torture/smb2/ea.c

## Purpose

This file defines the `SMB2-EA` torture suite for extended attribute behavior, currently focused on ensuring Samba's NT ACL backing xattr is not exposed or writable through SMB2 EA operations. The test protects the boundary between internal server metadata stored in xattrs and client-visible SMB extended attributes.

## Important APIs, Types, And Functions

`find_returned_ea()` scans a `union smb_fileinfo` result from `RAW_FILEINFO_SMB2_ALL_EAS` and returns true when the requested EA name appears. It handles null EA names and uses `strequal()` because Windows may capitalize returned EA names.

`torture_smb2_acl_xattr()` is the only test case. It uses `torture_setting_string(tctx, "acl_xattr_name", NULL)` to obtain the server's configured ACL xattr name, creates a test directory and file, sets a normal EA named `void`, lists all EAs, verifies the ACL xattr name is absent, and then attempts to set the protected ACL xattr directly.

The test uses `struct ea_struct` for EA name/value pairs, `union smb_setfileinfo` with `RAW_SFILEINFO_FULL_EA_INFORMATION` for setting EAs, and `union smb_fileinfo` with `RAW_FILEINFO_SMB2_ALL_EAS` for listing EAs. It relies on `data_blob_string_const()` for test EA payloads and `smb2_getinfo_file()` / `smb2_setinfo_file()` for SMB2 query and set operations.

## Control Flow

The test deletes `BASEDIR`, recreates it through `torture_smb2_testdir()`, creates `BASEDIR\\test_acl_xattr`, and writes a benign EA named `void` so the all-EA query has data to enumerate. It then queries `RAW_FILEINFO_SMB2_ALL_EAS` and fails if `find_returned_ea()` sees the configured ACL xattr name. Finally it builds a new full-EA set request for the protected ACL xattr name and expects `NT_STATUS_ACCESS_DENIED`.

All assertions use `torture_assert_*_goto()` so failures jump to a shared cleanup block. The cleanup closes the handle if it is non-empty and deletes `BASEDIR`.

## State And Persistence Behavior

The only persistent filesystem state is a temporary directory named `test_ea`, a test file, and a benign EA value. The suite must not persist the protected ACL xattr through SMB2. The core persistence assertion is negative: server-private NT ACL xattr storage must remain invisible in all-EA enumeration and must reject client writes.

The required `acl_xattr_name` torture setting couples the test to the server configuration. Missing configuration is a hard assertion failure because the test cannot know which EA name to protect without it.

## Dependencies And Integration Points

This file depends on Samba's SMB2 torture helpers, NTSTATUS definitions, SMB2 call wrappers, and talloc-backed data blobs. The suite is registered by `torture_smb2_ea()` with `torture_suite_add_1smb2_test(suite, "acl_xattr", torture_smb2_acl_xattr)`.

The test integrates with server configurations that store NT ACLs in an xattr, typically using an `acl_xattr_name` torture option aligned with the VFS module's actual private xattr name. It exercises the SMB2 EA query/set path, not direct POSIX xattr APIs.

## Risks And Edge Cases

The test's accuracy depends on `acl_xattr_name` matching the server-side private metadata name. A wrong or missing option can either fail setup or check the wrong EA. Case handling is intentionally tolerant through `strequal()`, but namespace prefixes and server-specific xattr name formats still matter.

The assertion message for the benign EA set says "Setting EA should fail" even though the expected status is OK; this is only a misleading message string and not the asserted behavior.

Because the test first sets a normal EA, environments that disallow user EAs entirely will fail before reaching the ACL leak checks. Such a failure indicates the test share is not suitable for this case rather than proving ACL xattr exposure.

## Test Signals

Passing signals are: normal EA set succeeds, all-EA query succeeds, the configured ACL xattr name is absent from returned EAs, and direct set of that ACL xattr returns `NT_STATUS_ACCESS_DENIED`.

Failure signals are especially important if the ACL xattr appears in `RAW_FILEINFO_SMB2_ALL_EAS` output or if `smb2_setinfo_file()` can write that protected name. Either result would expose or corrupt server-private security metadata through the SMB2 EA interface.

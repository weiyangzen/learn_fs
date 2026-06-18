# sources/user-network-fs/samba/source4/torture/smb2/util.c

## Purpose
`util.c` provides shared helper functions for Samba's SMB2 torture tests. It centralizes file and directory creation, SMB2 connection setup, tree/session setup, read/write utilities, metadata dump and verification helpers, lease/oplock/create request builders, and privilege checks so individual tests can focus on protocol behavior.

## Important APIs, Types, and Functions
Core file helpers include `smb2_util_write()`, `smb2_create_complex_file()`, `smb2_create_complex_dir()`, `smb2_create_simple_file()`, `torture_smb2_testfile_access()`, `torture_smb2_testfile()`, `torture_smb2_open()`, `torture_smb2_testdir_access()`, `torture_smb2_testdir()`, `torture_setup_simple_file()`, `torture_setup_complex_file()`, `torture_setup_complex_dir()`, `smb2_util_roothandle()`, and `smb2_util_setup_dir()`. Diagnostic and verification helpers include `torture_smb2_all_info()`, `torture_smb2_get_allinfo_access()`, `smb2_util_verify_sd()`, and `smb2_util_verify_attrib()`.

Connection helpers include `torture_smb2_tree_connect()`, `torture_smb2_session_setup()`, `torture_smb2_connection_ext()`, `torture_smb2_connection()`, `torture_smb2_con_share()`, and `torture_smb2_con_sopt()`. Lease/oplock helpers include `smb2_util_lease_state()`, `smb2_util_lease_state_string()`, `smb2_util_share_access()`, `smb2_util_oplock_level()`, `smb2_generic_create_share()`, `smb2_generic_create()`, `smb2_lease_create_share()`, `smb2_lease_create()`, `smb2_lease_v2_create_share()`, `smb2_lease_v2_create()`, `smb2_oplock_create_share()`, and `smb2_oplock_create()`.

## Control Flow
Simple helpers build a request struct, call the relevant SMB2 API, and return either an `NTSTATUS` or boolean. `smb2_create_complex()` is the most involved path: it removes a prior object, prepares a file or directory create request, optionally adds EAs, retries without EAs if unsupported, writes sample data for files, sets deliberately distinct timestamps, then queries all information to verify that the server stored the requested times.

Connection setup reads `host`, `share`, and optional `unclist` torture settings, pulls SMB client options and credentials from the command-line context, creates transports/sessions/trees, and reports failures through `torture_comment()`. Generic create builders populate `struct smb2_create` consistently for lease, oplock, directory, share-access, and disposition scenarios.

## State and Persistence Behavior
These helpers mutate remote SMB shares by creating, deleting, writing, and setting metadata on files and directories. They also allocate talloc contexts tied to trees or the torture context and return open SMB2 handles that callers must close. Connection helpers create client transport/session/tree state and may advance `tctx->conn_index` when `unclist` is used.

## Dependencies and Integration Points
The file sits at the center of SMB2 torture integration. It depends on SMB2 client calls, `smbXcli_base`, command-line credentials, loadparm, resolver and event contexts, security descriptor and NDR printing helpers, LSA privilege helpers, and `source4/torture/util.h`. Many SMB2 tests depend on these helpers through generated declarations in `torture/smb2/proto.h`.

## Risks
Because this file defines common request defaults, a change can alter many unrelated torture suites. The complex-file helper assumes timestamp setting support and reports errors if backends round or omit times. Attribute verification masks archive and non-indexed bits, which is intentional but can hide some server differences. Connection helpers depend on global command-line state and must be used with the correct talloc ownership.

## Test Signals
Signals produced by this file are usually helper-level `NTSTATUS` returns, torture comments, descriptor/attribute mismatch warnings, and failed assertions inside callers. For connection helpers, inability to connect or perform tree/session setup is an immediate test setup failure.

# sources/user-network-fs/samba/source4/torture/raw/mkdir.c

## Purpose
`mkdir.c` defines the raw SMB mkdir/rmdir torture test. It validates `RAW_MKDIR_MKDIR`, `RAW_MKDIR_T2MKDIR`, `RAW_RMDIR`, path validation, file-versus-directory errors, and extended attribute creation behavior.

## Important APIs, Types, and Functions
- `test_mkdir()` is the full test body.
- `torture_raw_mkdir()` is the exported entry point.
- Uses `union smb_mkdir`, `struct smb_rmdir`, `smb_raw_mkdir()`, `smb_raw_rmdir()`, `create_complex_file()`, `torture_check_ea()`, `smbcli_unlink()`, `smb_raw_exit()`, and `smbcli_deltree()`.
- `CHECK_STATUS` validates exact NT status codes and jumps to cleanup.

## Control Flow
The test creates `\\mkdirtest`, creates `\\mkdirtest\\mkdir.dir`, verifies duplicate mkdir collision, removes it, verifies missing rmdir, creates a file at the same path and verifies mkdir collision plus `rmdir` returning `NT_STATUS_NOT_A_DIRECTORY`, tests invalid relative traversal path syntax, creates via T2 mkdir, checks a bad nested path, then creates a directory with three EAs and validates those EAs unless Samba3 reports EAs unsupported.

## State and Persistence Behavior
All state is temporary under `\\mkdirtest`. EA values are allocated from the torture context with `data_blob_talloc()`. Cleanup exits the SMB session and deletes the whole test directory.

## Dependencies and Integration Points
This file integrates with the raw torture harness via `torture_raw_mkdir()`. It relies on raw SMB mkdir/rmdir marshalling and shared torture utility functions for directory setup, complex file creation, and EA verification.

## Risks and Edge Cases
- EA support is server-dependent; Samba3 `NT_STATUS_EAS_NOT_SUPPORTED` is explicitly non-fatal.
- The invalid path expectation is exact (`NT_STATUS_OBJECT_PATH_SYNTAX_BAD`) and may expose server dialect differences.
- `create_complex_file()` failure would feed an invalid fnum to `smbcli_close()` if not guarded by the helper's contract.

## Test Signals
Pass/fail is dominated by exact status checks for create, collision, removal, invalid path, T2 mkdir, and EA verification. Diagnostic prints identify each scenario.

# sources/user-network-fs/samba/source4/torture/smb2/setinfo.c

## Purpose

`setinfo.c` is a focused SMB2 torture test for individual `SETINFO` file information classes. It verifies that Samba/SMB2 servers accept, reject, and persist file metadata changes according to protocol expectations by setting values with `smb2_setinfo_file()` and reading them back with `smb2_getinfo_file()` or security/EA helpers. The exported test entry point is `torture_smb2_setinfo()`, registered by the top-level SMB2 suite as the simple test `smb2.setinfo`.

## Important APIs, Types, and Functions

The file uses `struct smb2_tree`, `struct smb2_handle`, `union smb_fileinfo`, `union smb_setfileinfo`, `struct security_descriptor`, `struct security_ace`, `struct dom_sid`, and `struct ea_struct`. SMB2 helper APIs include `torture_smb2_connection()`, `smb2_create_complex_file()`, `smb2_setinfo_file()`, `smb2_getinfo_file()`, `torture_smb2_all_info()`, `smb2_util_verify_sd()`, `smb2_util_close()`, and `smb2_util_unlink()`.

`find_returned_ea()` scans `SMB2_ALL_EAS` results, comparing EA names case-insensitively because Windows capitalizes returned EA names. Local assertion macros drive the test: `RECREATE_FILE` opens a fresh file handle, `CHECK_CALL` sets `RAW_SFILEINFO_*` and checks the expected status, `CHECK1` reads a matching `RAW_FILEINFO_*` level, `CHECK_VALUE` and `CHECK_TIME` compare returned fields, and `CHECK_STATUS` validates security descriptor mutation helpers.

## Control Flow

The test creates a temporary file name from the current time and opens it once through `RECREATE_BOTH`. It first dumps all info for diagnostics, then walks through set-info classes:

- `BASIC_INFORMATION` sets create/access/write/change times and attributes, verifies them via `SMB2_ALL_INFORMATION`, confirms zero times mean "do not change", confirms zero attributes mean "do not change", rejects changing a file into a directory, and restores normal attributes.
- `DISPOSITION_INFORMATION` toggles `delete_on_close` and verifies `delete_pending` and link count changes.
- `ALLOCATION_INFORMATION` and `END_OF_FILE_INFORMATION` set allocation and EOF sizes and verify returned all-info size fields.
- `POSITION_INFORMATION` sets the file pointer and checks both direct position info and all-info position.
- `MODE_INFORMATION` accepts valid modes, rejects an invalid mode value, and verifies returned mode.
- `SEC_DESC` reads owner/group/DACL, adds an `Authenticated Users` ACE, writes the descriptor, verifies it, then removes the ACE and verifies again.
- `FULL_EA_INFORMATION` sets, deletes, and attempts a zero-length EA while validating returned EAs.

All failures report the location and either jump to `done` or mark `ret = false`. Cleanup closes the handle and unlinks the file.

## State and Persistence Behavior

This test deliberately mutates on-disk file metadata: timestamps, DOS attributes, delete disposition, allocation size, EOF, current position, mode flags, DACL contents, and extended attributes. It expects changes to be immediately visible through subsequent `GETINFO` calls on the same handle. The security descriptor changes are restored by deleting the added ACE before cleanup. The EA section verifies SMB2-specific behavior: setting a non-empty EA creates it, setting the same EA with a null blob deletes it, and creating a zero-length EA should not leave a visible `ZeroEA` entry while pre-existing EAs such as `EAONE` and `SECONDEA` remain visible.

## Dependencies and Integration Points

The test depends on SMB2 get/set-info marshalling, security descriptor NDR types, Samba SID helpers, DACL mutation helpers, EA data blob handling, NT time conversions, and torture reporting. It is invoked from `torture_smb2_init()` in `smb2.c`. It assumes the target share supports setting file metadata, security descriptors, and EAs; filesystems or VFS modules without EA/security-descriptor support may produce meaningful failures or need environment-specific skips elsewhere.

## Risks

The test is sensitive to filesystem timestamp precision and semantics, though the base time is even-aligned to reduce rounding issues. Security descriptor verification can vary with share ACL configuration, filesystem ACL backends, inherited ACE behavior, or privilege restrictions. EA expectations are protocol-specific and include Windows name capitalization behavior; backend EA normalization or missing EA support can create false failures. The time-derived file name is less collision-resistant than the random names used elsewhere, but the collision window is small and cleanup unlinks the file.

## Test Signals

Useful signals are exact success/failure statuses per `RAW_SFILEINFO_*` level, read-after-write comparisons through `SMB2_ALL_INFORMATION`, security descriptor round-trip verification, and the positive/negative EA presence checks. Diagnostic calls to `torture_smb2_all_info()` and location-aware failure messages make regressions easier to isolate.

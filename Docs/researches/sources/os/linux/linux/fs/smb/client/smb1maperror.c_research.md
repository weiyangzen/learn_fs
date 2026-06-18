# File Research: sources/os/linux/linux/fs/smb/client/smb1maperror.c

This file maps SMB1/DOS/NT status errors to Linux `errno` values.

Key structures:
- `mapping_table_ERRDOS[]` and `mapping_table_ERRSRV[]` are generated tables mapping DOS/SRV SMB error codes to POSIX errors.
- `ntstatus_to_dos_map[]` is a generated sorted table mapping NT status codes to DOS class/code pairs.

Lookup logic:
- Uses `__inline_bsearch()` with small comparator helpers to search sorted tables.
- `map_smb_to_linux_error()` returns 0 for success, translates NT status to DOS class/code when `SMBFLG2_ERR_STATUS` is set, then maps DOS or server class codes to POSIX errors.
- Special NT status exceptions override table behavior for `NT_STATUS_NOT_A_REPARSE_POINT` to `-ENODATA` and `NT_STATUS_PRIVILEGE_NOT_HELD` to `-EPERM`.
- Unmapped or hard-error class values fall back to `-EIO` and emit `smb_EIO2()` tracing.

Reconnect behavior:
- `map_and_check_smb_error()` wraps mapping and triggers reconnect when an old-style server error is `ERRSRV/ERRbaduid`, indicating a bad session uid.

Initialization and tests:
- `smb1_init_maperror()` checks that all generated tables are sorted ascending; this is required for binary search correctness.
- Under `CONFIG_SMB1_KUNIT_TESTS`, internal lookup functions and arrays are exported for the KUnit module.

Dependencies:
- Generated include files: `smb1_err_dos_map.c`, `smb1_err_srv_map.c`, and `smb1_mapping_table.c`.

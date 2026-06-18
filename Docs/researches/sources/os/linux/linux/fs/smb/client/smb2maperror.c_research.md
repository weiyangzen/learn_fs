# File Research: sources/os/linux/linux/fs/smb/client/smb2maperror.c

This file maps SMB2/NT status codes from server responses to Linux errno values.

Primary responsibilities:
- Include the generated `smb2_mapping_table.c` as `smb2_error_map_table`.
- Locate mapping entries by binary search.
- Convert SMB2 response status codes to POSIX errors in `map_smb2_to_linux_error()`.
- Validate mapping-table sort order at module initialization.
- Export test-only mapping symbols for KUnit when `CONFIG_SMB_KUNIT_TESTS` is enabled.

Important control flow:
- `cmp_smb2_status()` compares a searched status key with a `status_to_posix_error` table pivot.
- `smb2_get_err_map()` uses `__inline_bsearch()` over the sorted mapping table.
- `map_smb2_to_linux_error()` returns zero for successful SMB2 statuses and emits `trace_smb3_cmd_done()`.
- Nonzero statuses default to `-EIO` when no mapping exists.
- Logging suppresses noisy notices for `STATUS_MORE_PROCESSING_REQUIRED` and `STATUS_END_OF_FILE` unless CIFS FYI/error logging is enabled.
- Error paths trace `trace_smb3_cmd_err()` and call `smb_EIO1()` for unmapped `-EIO`.

Validation and safety:
- `smb2_init_maperror()` walks the generated mapping table and returns `-EINVAL` if the array is not sorted ascending by status code, which is required for binary search correctness.

Dependencies:
- Generated SMB2 mapping table, `struct status_to_posix_error` from `smb2glob.h`, SMB2 status constants, tracepoints, CIFS logging, and Linux errno values.

Research notes:
- The correctness of all SMB2 error handling depends on the generated table remaining sorted.
- The test-only exports are narrow and exist specifically so `smb2maperror_test.c` can verify binary-search coverage over every table entry.

# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2maperror.c

## Purpose
Maps SMB2/SMB3 NT status codes to Linux/POSIX errno values and emits associated logging/tracing.

## Main Responsibilities
- Define the SMB2 status-to-errno mapping table.
- Perform fast lookup by NT status code.
- Convert SMB2 response header status into Linux return codes.
- Validate mapping table sort order at init.
- Export internals for KUnit testing when SMB tests are enabled.

## Key Functions and Data
- `smb2_error_map_table[]` includes generated entries from `smb2_mapping_table.c`, sorted by CPU-endian NT status code.
- `cmp_smb2_status()` compares a search key against a table entry.
- `smb2_get_err_map()` uses `__inline_bsearch()` over the sorted table.
- `map_smb2_to_linux_error()` returns `0` for success, suppresses noisy logging for expected statuses, maps known statuses, defaults unknown statuses to `-EIO`, emits trace events, and records SMB EIO trace when mapping falls back to `-EIO`.
- `smb2_init_maperror()` verifies ascending table order at module/init time.
- KUnit-only exports provide access to lookup, table pointer, and table length.

## Important Data Flow
1. Caller passes an SMB2 response buffer.
2. Header `Status` is read as little-endian NT status.
3. Zero status emits success trace and returns `0`.
4. Non-zero status is searched in `smb2_error_map_table`.
5. Known statuses return their configured Linux errno; unknown statuses return `-EIO`.
6. Error tracepoints include TreeId, SessionId, Command, MessageId, NT status, and errno.

## Edge Cases and Defensive Logic
- `STATUS_MORE_PROCESSING_REQUIRED` and `STATUS_END_OF_FILE` avoid normal error logging unless CIFS return-code debugging is enabled.
- Table order is checked because binary search correctness depends on it.
- Unknown status codes deliberately degrade to `-EIO`.

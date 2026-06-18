# sources/user-network-fs/libsmb2/lib/errors.c

## Purpose
`errors.c` is libsmb2's central translation table for SMB2/NTSTATUS failures. It exposes readable NT status names for diagnostics and converts selected server status codes into POSIX `errno` values that higher-level sync and async APIs can return to callers.

## Important APIs, Types, and Functions
The file exports `nterror_to_str(uint32_t status)` and `nterror_to_errno(uint32_t status)`. Both consume status constants from `smb2.h`, primarily `SMB2_STATUS_*` values. `nterror_to_str()` is a large switch returning static string literals. `nterror_to_errno()` maps a curated subset of SMB2 status codes to system errors such as `ENOENT`, `EACCES`, `EBADF`, `EINVAL`, `ENETRESET`, and `EIO`.

## Control Flow
`nterror_to_str()` performs one direct switch over the status code. Known codes return immediately; unknown codes fall through to `"Unknown"`. `nterror_to_errno()` also uses a switch, but groups semantically related statuses: missing path/object statuses become `ENOENT`, invalid handles become `EBADF`, authentication restrictions become `EACCES`, retryable transport/session tear-down statuses become `ENETRESET`, and the default is `EIO`. `SMB2_STATUS_SUCCESS` and `SMB2_STATUS_END_OF_FILE` intentionally map to zero.

## State and Persistence Behavior
The file has no mutable static state and performs no allocation or persistence. All outputs are deterministic for the input status and the platform's `errno` macro definitions. Returned strings are static literals and must not be freed.

## Dependencies and Integration Points
It depends on `errno.h`, optional platform headers from `config.h`, `compat.h`, and libsmb2 status definitions in `smb2.h`. It is used wherever libsmb2 reports protocol errors through `smb2_set_nterror()`, callback statuses, or POSIX-style API return paths.

## Risks and Edge Cases
The string mapper is manually maintained and may lag new status constants. Some returned names include the `SMB2_` prefix while others use Windows-style `STATUS_`, which can matter for logs or tests that compare strings exactly. Unknown status values are collapsed to `"Unknown"` and `EIO`, losing diagnostic precision. A few mappings are policy choices rather than exact POSIX equivalents, such as `STATUS_PATH_NOT_COVERED` to `ENOEXEC` and several disconnect/reset statuses to `ENETRESET` to encourage retry handling.

## Test Signals
Useful tests should cover representative status groups, not every switch arm: success/EOF to zero, missing paths to `ENOENT`, invalid handles to `EBADF`, access failures to `EACCES`, retryable disconnects to `ENETRESET`, unknown values to `EIO`/`"Unknown"`, and exact string names for high-frequency statuses such as `STATUS_ACCESS_DENIED`, `STATUS_LOGON_FAILURE`, `STATUS_SHARING_VIOLATION`, and `STATUS_BAD_NETWORK_NAME`.

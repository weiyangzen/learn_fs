# File Research: sources/virtualization/open-iscsi/usr/iscsi_err.c

This small file defines open-iscsi's global error variable and maps open-iscsi error codes to human-readable messages.

Key contents:
- Global `enum iscsi_error_list iscsi_err`.
- Static `iscsi_err_msgs[]` table indexed by numeric error value.
- `iscsi_err_to_str(int err)` returns the message string or logs and returns NULL for invalid codes.
- `iscsi_err_print_msg(int err)` logs a formatted initiator error message or logs invalid-code input.

Important dependencies:
- Includes `iscsi_err.h` for error enum/max value.
- Includes `log.h` for `log_error()`.

Filesystem/storage relevance:
- Provides user/admin-facing diagnostics for iSCSI session, discovery, IPC, sysfs, auth, and target connection failures.

Notable constraints:
- The table must stay aligned with `enum iscsi_error_list` and `ISCSI_MAX_ERR_VAL`.
- Invalid errors are logged rather than mapped to a fallback string.

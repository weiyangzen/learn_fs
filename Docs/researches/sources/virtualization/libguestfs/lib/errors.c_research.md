# File Research: sources/virtualization/libguestfs/lib/errors.c

Purpose: Implements libguestfs error storage, error callbacks, warning/debug/trace message emission, buffer trace formatting, and standardized launch/external-command failure messages.

Key behavior:
- Uses per-handle pthread TLS (`g->error_data`) so each thread has its own last error, errno, and error handler stack while sharing one `guestfs_h`.
- Maintains `g->error_data_list` so all per-thread error records can be freed when the handle closes.
- `guestfs_int_error_errno` and `guestfs_int_perrorf` format messages, update last error first, then invoke the current callback.
- Warning/debug/trace messages are routed through the event callback system as `GUESTFS_EVENT_WARNING`, `GUESTFS_EVENT_LIBRARY`, and `GUESTFS_EVENT_TRACE`.
- `guestfs_int_print_BufferIn/Out` truncates trace output for large binary buffers to 256 bytes.
- Standard helpers produce user-facing diagnostics for launch failure, unexpected appliance close, launch timeout, and failed external commands.

Dependencies and state:
- Depends on `guestfs-internal.h` macros (`error`, `perrorf`, locks), `events.c` callback dispatch, pthread TLS, and safe allocation helpers.
- Mutates `g->error_data_list`, per-thread `struct error_data`, `g->abort_cb`.

Risks:
- `set_last_error` uses `strdup` directly; allocation failure leaves `last_error` NULL without invoking the abort callback.
- Callers must follow the file’s rule to set exactly one error per error path, otherwise earlier errors are overwritten.

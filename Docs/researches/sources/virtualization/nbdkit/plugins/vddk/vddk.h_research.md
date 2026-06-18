# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk.h

Shared internal header for the VDDK plugin.

Key contents:
- Includes VDDK local struct definitions and common helpers.
- Declares global plugin configuration/state shared across `vddk.c`, `worker.c`, `reexec.c`, `stats.c`, and `utils.c`.
- Declares VDDK function pointers through `vddk-stubs.h`.
- Defines `VDDK_CALL_START`, `VDDK_CALL_END`, and `VDDK_CALL_END_ASYNC` macros for debug logging and stats timing around VDDK API calls.
- Defines `VDDK_ERROR` wrapper that converts a `VixError` to text via VDDK and logs it.
- Defines command types for worker-thread execution: `INFO`, `READ`, `WRITE`, `FLUSH`, `CAN_EXTENTS`, `EXTENTS`, `STOP`.
- Defines `struct command`, including request fields, generated serial id, timing, mutex/condition, and completion status.
- Defines `command_queue` vector type.
- Defines per-connection `struct vddk_handle`, including VDDK params/connection/handle, worker thread, command queue, filename, readonly flag, cached disk size, and cached extents.
- Declares reexec, stats, utility, and worker functions.
- Defines inline `update_stats`, protected by `stats_lock`.

Role:
- Centralizes plugin-wide state and the command protocol between nbdkit callback threads and the VDDK worker thread.

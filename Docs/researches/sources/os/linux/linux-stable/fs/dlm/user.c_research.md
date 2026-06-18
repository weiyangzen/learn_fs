# File Research: sources/os/linux/linux-stable/fs/dlm/user.c

## Purpose
`user.c` implements the userspace DLM misc-device interface. It lets userspace create/remove lockspaces, issue lock/unlock/cancel/deadlock/purge commands, and read AST/BAST completion events.

## Device Model
The file registers:
- `dlm-control`: control device for creating/removing lockspaces and reading version.
- `dlm-monitor`: monitor device used to detect daemon availability and stop lockspaces when the monitor closes.
- Per-lockspace devices named `dlm_<lockspace>`.

Each opener of a lockspace device gets a `struct dlm_user_proc` that tracks owned locks and pending callbacks for that process.

## User Request Handling
`device_write()` validates request size/version, handles compat conversion when needed, rejects lock operations on closing processes, and dispatches:
- `DLM_USER_LOCK`
- `DLM_USER_UNLOCK`
- `DLM_USER_DEADLOCK`
- `DLM_USER_CREATE_LOCKSPACE`
- `DLM_USER_REMOVE_LOCKSPACE`
- `DLM_USER_PURGE`

Lock requests allocate `struct dlm_user_args` and call lower lock-layer helpers:
- `dlm_user_request()`
- `dlm_user_convert()`
- `dlm_user_adopt_orphan()`
- `dlm_user_unlock()`
- `dlm_user_cancel()`
- `dlm_user_deadlock()`
- `dlm_user_purge()`

## Callback Delivery
`dlm_user_add_ast()` queues user-visible callbacks unless the lock is orphaned/dead or the callback can be skipped. It copies callback state into `struct dlm_callback`, optionally copies LVB data, wakes the process waitqueue, and removes end-of-life locks from the process lock list.

A lock becomes end-of-life for noqueue failures, unlock completion, and cancel/deadlock/timeout cases involving an IV-mode request.

`device_read()` returns one callback as `struct dlm_lock_result`, optionally followed by LVB bytes. Reads of exactly `struct dlm_device_version` return only version information.

## Process Lifecycle
`device_open()` creates a `dlm_user_proc` and takes a lockspace reference. `device_close()` marks the proc closing, calls `dlm_clear_proc_locks()`, frees proc state, and drops both the open-time and local lookup references.

## Compat Support
Under `CONFIG_COMPAT`, the file converts 32-bit write requests and lock results to/from native structures, including user pointer fields.

## Daemon Availability
`dlm_user_daemon_available()` reports availability based on configured local node id and whether the monitor device is opened, while preserving compatibility with older `dlm_controld` that never opened the monitor.

## Risks and Notes
The user path is sensitive to callback lifetime: `ls_clear_proc_locks` prevents AST delivery from racing with process cleanup. Device input size/version checks are the primary boundary for userspace command parsing.

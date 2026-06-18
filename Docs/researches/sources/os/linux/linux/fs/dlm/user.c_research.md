# File Research: sources/os/linux/linux/fs/dlm/user.c

## Role

`user.c` implements the DLM userspace character-device interface. It provides the control device for lockspace create/remove, per-lockspace devices for lock/unlock/deadlock/purge operations, AST/BAST callback delivery, compat translation, and monitor-device integration with `dlm_controld`.

## Compat Support

Under `CONFIG_COMPAT`, 32-bit request/result structures are translated by `compat_input()` and `compat_output()`. Lock parameter pointers and callback addresses are widened from 32-bit user values.

## Callback Delivery

`dlm_user_add_ast()` adds completion or blocking callbacks to the owning process queue unless the lock is orphaned/dead or the callback can be skipped. End-of-life locks are removed from the process lock list after final AST generation.

Callbacks copy LVB data into callback-local storage when needed so later user reads see stable data.

## User Commands

`device_write()` validates request size and device protocol version, translates compat input when needed, rejects lock operations during close, and dispatches:
- `DLM_USER_LOCK` to request/convert/adopt-orphan paths
- `DLM_USER_UNLOCK` to unlock/cancel
- `DLM_USER_DEADLOCK` to deadlock handling
- `DLM_USER_CREATE_LOCKSPACE` on control device
- `DLM_USER_REMOVE_LOCKSPACE` on control device
- `DLM_USER_PURGE` on lockspace devices

Create/remove lockspace operations require `CAP_SYS_ADMIN`.

## Device Lifecycle

`device_create_lockspace()` creates a user lockspace and registers a per-lockspace misc device named `dlm_<name>`. `dlm_device_deregister()` removes that misc device.

Opening a lockspace device creates a per-file `dlm_user_proc` with AST, lock, and unlocking lists. Closing marks the proc closing, clears process locks, frees the proc, and drops references held by open/find.

## Read and Poll

`device_read()` either returns the device version or waits for one callback from the process AST queue. It copies a `dlm_lock_result` or compat result to userspace, optionally followed by LVB data.

`device_poll()` reports readable state when ASTs are queued.

## Control and Monitor Devices

`dlm_user_init()` registers:
- `dlm-control` for create/remove and version reads
- `dlm-monitor` for daemon availability monitoring

`dlm_user_daemon_available()` treats a configured nodeid as enough for old daemons that never open monitor; otherwise it requires the monitor device to be open. Closing the last monitor fd calls `dlm_stop_lockspaces()`.

## Important Behaviors and Invariants

- User lock operations require a process context from a lockspace device, not the control device.
- Create/remove require the control device, not a lockspace device.
- Protocol major must match and user minor cannot exceed kernel minor.
- AST queues are per open file, so each process sees callbacks for its own locks.
- `ls_clear_proc_locks` protects AST delivery against process lock cleanup.

## Research Notes

Read completely. This is the primary userspace DLM API implementation and coordinates with lock, AST, config, and lockspace code.

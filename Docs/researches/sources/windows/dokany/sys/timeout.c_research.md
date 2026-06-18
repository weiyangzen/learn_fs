# File Research: sources/windows/dokany/sys/timeout.c

Implements pending IRP timeout handling, timeout reset, timeout worker thread lifecycle, and unmount-on-timeout behavior.

Key entry points:
- `DokanUnmount()` invokes `DokanEventRelease()` for the DCB's VCB.
- `ReleaseTimeoutPendingIrp()` scans pending IRPs, removes timed-out or async-failed entries, cancels/finishes them, and may unmount before keepalive activation.
- `DokanResetPendingIrpTimeout()` updates a pending IRP timeout from a user-mode `EVENT_INFORMATION` reset request.
- `DokanTimeoutThread()` waits on kill, force-timeout, or periodic timer events and runs timeout release unless the system appears to have resumed from sleep.
- `DokanStartCheckThread()` and `DokanStopCheckThread()` manage the timeout thread.
- `DokanUpdateTimeout()` converts a millisecond timeout into a future tick count.

Core mechanics:
- Pending IRPs normally time out when current tick count reaches `IRP_ENTRY.TickCount`.
- `AsyncStatus` allows async operations such as cancellation/oplock failure to reuse timeout cleanup with a specific failure status.
- Forced-canceled create IRPs are always effectively canceled in this timeout path.
- Non-create IRPs race with cancel routines through `IoSetCancelRoutine(NULL)`; if cancellation is already running, memory ownership is handed to the cancel routine.
- Timed-out create IRPs call `DokanCancelCreateIrp()` with `STATUS_CANCELLED` if explicitly canceled or `STATUS_INSUFFICIENT_RESOURCES` if timed out.
- Timed-out cleanup IRPs execute cleanup before completion.
- If any IRP times out before keepalive activation, Dokan unmounts the filesystem to avoid repeated Explorer delays.
- Sleep/resume detection skips timeout processing when the periodic timer was delayed far beyond the check interval.

Important invariants:
- Pending list scanning is protected by `Dcb->PendingIrp.ListLock`.
- Cancel routines are cleared before completing IRPs outside the list.
- `DRIVER_CONTEXT_IRP_ENTRY` is cleared before completion to prevent later cancel-routine action.
- Timeout reset caps values at `DOKAN_IRP_PENDING_TIMEOUT_RESET_MAX`.
- Stop waits for the timeout thread and dereferences its object.

Filesystem relevance:
- This file enforces liveness for user-mode filesystem operations. It prevents abandoned pending IRPs from hanging indefinitely and triggers unmount when the user-mode side fails during startup.

Notable risks:
- Timeout completion paths overlap with user-mode replies and cancel routines, making ownership transitions subtle.
- Sleep detection intentionally avoids false timeout storms after resume.
- Pre-keepalive unmount changes mount lifecycle based on early operation timeouts.

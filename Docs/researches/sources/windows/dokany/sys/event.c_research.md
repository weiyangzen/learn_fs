# File Research: sources/windows/dokany/sys/event.c

Implements Dokan's central kernel/user event IPC path: pending IRP registration, cancellation, completion from user mode, mount start, replacement-drive handling, and large write event handoff.

Key entry points:
- `DokanRegisterPendingIrp()` registers a filesystem IRP on `Dcb->PendingIrp`, assigns a serial number, installs the cancel routine, and queues an `EVENT_CONTEXT` for user mode.
- `RegisterPendingIrpMain()` is the shared registration helper for normal pending IRPs, retry IRPs, and async create failures.
- `DokanCompleteIrp()` consumes one or more `EVENT_INFORMATION` replies from user mode, matches them by serial number, removes pending IRPs, handles forced-canceled create races, and dispatches to per-major completion routines.
- `DokanDispatchCompletion()` routes completed events to read, write, create, cleanup, query/set information, volume, lock, flush, and security completion handlers.
- `DokanEventStart()` handles `FSCTL_EVENT_START`, validates the user-mode version and mount inputs, creates a disk/network device, inserts a mount entry, starts notification support, verifies/mounts the volume, and returns `EVENT_DRIVER_INFO`.
- `DokanEventWrite()` provides the second-stage transfer path for large write event contexts.
- `DokanCreateIrpCancelRoutine()` and `DokanIrpCancelRoutine()` handle create-specific cancellation via timeout wakeup and non-create cancellation directly.
- `DokanOplockComplete()` and `DokanPrePostIrp()` bridge FsRtl oplock completion back into Dokan's pending-event flow.

Core mechanics:
- Pending IRPs carry `IRP_ENTRY` records linked into `IRP_LIST` instances with a timeout tick, serial number, copied `REQUEST_CONTEXT`, and async status.
- Create IRP cancellation is intentionally deferred to the timeout path because create cleanup is too complex for an arbitrary cancel-routine context.
- Non-create cancellation removes the IRP from its list, frees any saved write `EVENT_CONTEXT`, optionally executes cleanup at passive level, and completes with `STATUS_CANCELLED`.
- Completion batching is allowed only when `Dcb->AllowIpcBatching` is enabled; replies must be sorted by serial number.
- Invalid batched replies, oversized replies, or unexpected batching are treated as DLL misuse and can trigger unmount to avoid permanently hung requests.
- Mount startup normalizes drive-letter mount points to `\DosDevices\X:`, supports current-session mounts, mount-manager integration, write-protect/removable flags, case-sensitivity flags, alternate streams, user-mode file locks, driver log dispatch, IPC batching, and optional volume security descriptors.
- Existing Dokan drive replacement is allowed only when the old and new device owners match.

Important invariants:
- IRP state and driver-context pointers are initialized before a cancel routine is installed.
- Unmount state is checked before and after list locking to avoid registering IRPs that can never complete.
- The event context size must not exceed `EVENT_CONTEXT_MAX_SIZE`, except write uses a special two-step path.
- Once a cancel routine is observed as already running, ownership transfers to that routine or to forced-cancel handling.
- Mount entries are protected by global and per-entry resources and must be released in the right order.

Filesystem relevance:
- This file is the heart of Dokan's FUSE-like bridge. It decides when kernel filesystem IRPs are converted into user-mode operations, how replies complete original IRPs, and how a user-mode filesystem instance becomes a mounted Windows volume.

Notable risks:
- Completion batching is delicate: bad serial ordering or size calculation can leave requests unmatched, so the driver unmounts on detected misuse.
- Create cancellation has multiple race paths between user-mode reply, cancel routine, and timeout thread.
- Mount replacement depends on security descriptor owner comparison and mount-entry removal being accurate.

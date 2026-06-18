# File Research: sources/windows/winfsp/src/sys/wq.c

This file provides WinFsp’s helper path for deferring IRP processing to a system work queue.

Key responsibilities:
- Prepares IRPs before worker execution by locking user buffers for reads, writes, and directory queries when the IRP is not using the MDL minor path.
- Creates or augments an `FSP_FSCTL_TRANSACT_REQ` with an embedded work item.
- Stores the target `FSP_IOP_REQUEST_WORK` routine and initializes the `WORK_QUEUE_ITEM`.
- Optionally posts the work item immediately and returns `STATUS_PENDING`.
- Marks IRPs pending and queues work to `CriticalWorkQueue`.
- Runs the saved work routine with `CanWait=TRUE` from `FspWqWorkRoutine`.
- Completes the IRP directly when the routine returns an ordinary status.
- Posts the IRP to the fsvol IOQ when the work routine returns WinFsp private queue-post statuses.

Important dependencies:
- `FspLockUserBuffer` for safe user-buffer access after deferral.
- `FspIopCreateRequestAndWorkItem`, `FspIopCreateRequestWorkItem`, and `FspIopRequestWorkItem`.
- `FspIoqPostIrpEx` for handing a deferred IRP back to the user-mode transaction queue.
- `FspIopCompleteIrp` for final completion.
- Top-level IRP management via `IoSetTopLevelIrp`.

Filesystem relevance:
- This is a small but important scheduling shim for operations that cannot complete immediately, often because they need a waitable context.
- It is used by paths such as cached/non-cached I/O retry handling to move work out of the original dispatch context without losing the IRP/request association.

Notable watchpoints:
- The helper asserts that the request finalizer matches the request header, so callers must preserve finalizer consistency when reusing requests.
- Debug assertions restrict queued major functions to create, read, write, directory control, and lock control.
- Private status handling assumes only `FSP_STATUS_IOQ_POST` and `FSP_STATUS_IOQ_POST_BEST_EFFORT` are valid queue-post outcomes.

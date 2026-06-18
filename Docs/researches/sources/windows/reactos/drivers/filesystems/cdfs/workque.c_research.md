# File Research: sources/windows/reactos/drivers/filesystems/cdfs/workque.c

Implements request posting and overflow work-queue handling for CDFS FSD-to-FSP transitions and oplock completion.

Key entry points:
- `CdFsdPostRequest()` prepares an IRP for pending processing and queues it to the FSP work queue.
- `CdPrePostIrp()` locks user buffers where needed, performs create-path teardown cleanup, cleans the IRP context for posting, and marks the IRP pending.
- `CdOplockComplete()` resumes oplock-blocked IRPs by queueing successful ones or completing failed ones.
- `CdAddToWorkque()` sends work to an executive worker thread or a per-volume overflow queue.

Core mechanics:
- Posted creates may carry a `TeardownFcb`; this is torn down before the request is posted so create cleanup will not release stale state.
- Read, write, and query-directory requests lock the user buffer before returning pending, unless the operation is MDL-based.
- `IRP_CONTEXT_FLAG_MORE_PROCESSING` keeps the IRP context alive across posting while clearing per-thread/top-level state.
- Per-volume throttling sends more than two active posted requests to an overflow queue protected by `OverflowQueueSpinLock`.
- Work items are queued to `CriticalWorkQueue` and dispatch through `CdFspDispatch`.

Important invariants:
- User buffers must be locked before `STATUS_PENDING` returns to the caller.
- Posted request accounting is per volume device object when a file object is present.
- Oplock completion may run outside the original dispatch context and must either queue or complete the IRP.

Filesystem relevance:
- Provides the async/blocking escape path for operations that cannot complete in the current FSD thread.
- Integrates oplock waits with normal CDFS worker-thread dispatch.

Notable risks:
- Overflow queue draining is handled elsewhere; this file only enqueues overflow work.
- Read and write buffer locking both reference `IrpSp->Parameters.Read.Length`; this relies on the read/write parameter union layout.

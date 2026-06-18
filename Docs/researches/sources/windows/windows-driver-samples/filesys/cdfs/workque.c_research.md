# File Research: sources/windows/windows-driver-samples/filesys/cdfs/workque.c

## Purpose

Implements CDFS request posting from the FSD path to worker-thread/FSP processing. It prepares IRPs for asynchronous continuation, handles oplock completion reposting, and throttles per-volume work items with an overflow queue.

## Key routines

- `CdFsdPostRequest`: common FSD posting entry point. Calls `CdPrePostIrp`, enqueues through `CdAddToWorkque`, and returns `STATUS_PENDING`.
- `CdPrePostIrp`: performs pre-post cleanup. It locks user buffers for reads, writes, and directory queries; handles create teardown state from oplock paths; marks the IRP pending; sets `IRP_CONTEXT_FLAG_MORE_PROCESSING`; and cleans the IRP context for reposting.
- `CdOplockComplete`: oplock package callback. If the IRP completed successfully, performs create teardown cleanup and queues the request; otherwise completes the request with the IRP status.
- `CdAddToWorkque`: queues the IRP context either to the per-volume overflow queue or to `CriticalWorkQueue` using `ExInitializeWorkItem` / `ExQueueWorkItem`.

## Control flow and state

`CdAddToWorkque` derives the `VOLUME_DEVICE_OBJECT` from the current IRP stack device object when a file object exists. It uses `OverflowQueueSpinLock` to guard `PostedRequestCount`, `OverflowQueue`, and `OverflowQueueCount`. If `PostedRequestCount > FSP_PER_DEVICE_THRESHOLD` where the threshold is `2`, it appends the context to the volume overflow list. Otherwise it increments `PostedRequestCount` and queues a worker item to `CdFspDispatch`.

`CdPrePostIrp` is also careful about create-time teardown state. When `IrpContext->TeardownFcb` still names an FCB, it calls `CdTeardownStructures`, releases the FCB if the teardown did not remove it, then clears both the referenced pointer and `IrpContext->TeardownFcb`.

## Dependencies

This file depends on CDFS core types and helpers from `CdProcs.h`, including `PIRP_CONTEXT`, `CdCleanupIrpContext`, `CdLockUserBuffer`, `CdTeardownStructures`, `CdReleaseFcb`, `CdCompleteRequest`, and `CdFspDispatch`. It also uses Windows kernel IRP, work queue, spin lock, and cache-safe pending APIs.

## Edge cases and notes

- MDL reads/writes skip user-buffer locking because no user buffer is present.
- Query-directory requests lock the query output buffer for write access.
- Failed oplock completion does not repost; it completes immediately.
- Requests with no associated file object bypass per-volume throttling and are queued directly to the system work queue.
- The file suppresses PREfast/obsolete warnings around legacy `ExInitializeWorkItem` and `ExQueueWorkItem`.

# File Research: sources/windows/reactos/drivers/filesystems/cdfs/close.c

## Purpose

`close.c` implements `IRP_MJ_CLOSE` and CDFS deferred close processing. Close releases final file-object references, decrements FCB/VCB reference counts, and triggers structure teardown when possible. It supports immediate, async, and delayed close paths.

## Key Contents

- Local helpers:
  - `CdCommonClosePrivate`
  - `CdQueueClose`
  - `CdRemoveClose`
  - `CdCloseWorker`

- `CdFspClose`
  - Processes async and delayed close queues.
  - If a VCB is supplied, drains closes for that VCB; otherwise processes normal queued work.
  - Converts `IRP_CONTEXT_LITE` delayed-close entries into a stack `IRP_CONTEXT`.
  - Extracts FCB/user-reference data from full async `IRP_CONTEXT` entries.
  - Sets FSP/top-level flags and thread context.
  - Batches close processing per VCB but periodically releases/reacquires to avoid starving exclusive VCB waiters.
  - Detects possible VCB teardown when the volume is no longer mounted and cleanup count is zero, rechecking under `CdData`.
  - Calls `CdCommonClosePrivate`.
  - Completes/cleans up each IRP context and releases held VCB/global locks.

- `CdCommonClose`
  - FSD entry point for close.
  - Completes immediately for filesystem-device-object requests and unopened file objects.
  - Decodes file object, deletes CCB if present, and treats CCB presence as one user reference.
  - If mounted volume, last FCB reference, and user file/directory open, queues delayed close.
  - Otherwise checks whether VCB teardown may be needed, acquiring `CdData` for safe dismount synchronization.
  - Calls `CdCommonClosePrivate`; if resources cannot be acquired without waiting, queues async close.
  - Always completes the original IRP with `STATUS_SUCCESS`.

- `CdCommonClosePrivate`
  - Acquires VCB shared and FCB exclusive.
  - In FSD path, acquisition may be non-waiting; failure returns `FALSE` so caller queues async close.
  - Decrements VCB/FCB reference counts using `CdDecrementReferenceCounts`.
  - Calls `CdTeardownStructures`.
  - Releases FCB if teardown did not remove it, then releases VCB.
  - Returns `TRUE` when close was processed.

- `CdCloseWorker`
  - Work-item trampoline that calls `CdFspClose(NULL)`.

- `CdQueueClose`
  - Queues either delayed or async close work.
  - Delayed close allocates `IRP_CONTEXT_LITE`; allocation failure falls back to async close.
  - Cleans up top-level request state before queueing.
  - Delayed queue stores compact FCB/user-reference/real-device data.
  - Async queue reuses the existing `IRP_CONTEXT`, storing FCB in `IrpContext->Irp` and user reference in `ExceptionStatus`.
  - Starts the close worker via `IoQueueWorkItem` when needed.
  - Triggers delayed-close reduction when count exceeds `CdData.MaxDelayedCloseCount`.

- `CdRemoveClose`
  - Removes a suitable close item from async queue first.
  - If no async item is found, optionally scans delayed queue when a VCB is specified or delayed reduction is active.
  - Filters by VCB when requested.
  - Disables `FspCloseActive` and `ReduceDelayedClose` when no work remains for normal processing.

## Dependencies and Interactions

- Uses close queue fields in `CD_DATA`: `AsyncCloseQueue`, `DelayedCloseQueue`, counts, thresholds, flags, and `CloseItem`.
- Depends on `IRP_CONTEXT_LITE`, `IRP_CONTEXT`, VCB/FCB reference counts, and teardown structures from `cdstruc.h`.
- Uses synchronization macros from `cdprocs.h`.
- Works with `cleanup.c`: cleanup decrements handle counts and share state; close decrements reference counts and can remove FCB/VCB structures.
- Dismount decisions call `CdCheckForDismount` and rely on VCB condition/cleanup state.

## Behavioral Notes

- Close always returns success to the I/O manager after queueing or processing because close failure is not surfaced as normal filesystem operation failure.
- Delayed close is an optimization for recently closed user files/directories on mounted volumes.
- Async close avoids unsafe waits or lock-order problems from FSD/recursive close paths.
- `CdCommonClosePrivate` is intentionally small: acquire, decrement, teardown, release.
- Queue storage is compact for delayed closes to avoid keeping full IRP contexts alive in a long-lived queue.

# File Research: sources/windows/reactos/drivers/filesystems/fastfat/close.c

## Purpose

`close.c` implements FastFAT `IRP_MJ_CLOSE`, the final reference-release phase for file objects. It tears down CCBs, decrements open counters, releases internal stream references, deletes unreferenced FCB/DCB structures, checks whether a volume can dismount, and manages asynchronous/delayed close queues so close work can be deferred when immediate resource acquisition would block or when cleanup marked an object for delayed close.

## Key Entry Points

- `FatFsdClose`
  - Top-level dispatch routine for close IRPs.
  - Immediately succeeds close sent to the filesystem device object instead of a mounted volume device object.
  - Decodes the file object, marks the CCB read-only when appropriate, handles close-without-cleanup oplock cleanup on Windows 8+ paths, preallocates close contexts for metadata streams, and either runs `FatCommonClose` synchronously or queues the close.

- `FatCloseWorker`
  - I/O work-item shim that enters the filesystem and calls `FatFspClose`.

- `FatFspClose`
  - Worker/FSP close-drain routine.
  - Removes queued close contexts and calls `FatCommonClose` with wait allowed.
  - When draining all volumes, tries to batch multiple closes under one VCB resource acquisition without holding the VCB across the final close that might delete the volume.

- `FatQueueClose`
  - Inserts a close context into either the async close list or delayed close list.
  - Maintains both global and per-VCB lists plus global counters.
  - Starts the close worker when async work is needed or delayed-close pressure exceeds `FatMaxDelayedCloseCount`.

- `FatRemoveClose`
  - Removes a close context from global or per-VCB close queues.
  - Gives priority to async closes, then delayed closes above threshold or during shutdown.
  - Uses high-water pressure flags to prefer closes for the last VCB when queues are well over limit.

- `FatCommonClose`
  - Common close implementation for all open types.
  - Builds a stack `IRP_CONTEXT`, acquires the VCB, handles create/close serialization, decrements open/reference counts, frees CCBs, deletes unreferenced FCB/DCB structures, and optionally triggers dismount.

## Close Dispatch and Queueing

- `FatFsdClose` uses `TopLevel && PsGetCurrentProcess() != FatData.OurProcess` to decide whether synchronous close may wait for the VCB.
- If `FatCommonClose` returns `STATUS_PENDING`, or a user file/directory FCB has `FCB_STATE_DELAY_CLOSE` and shutdown has not started, the close is queued and the IRP is completed successfully.
- Metadata stream opens (`VirtualVolumeFile`, `DirectoryFile`, `EaFile`) get a pool-allocated close context before close work starts because the VCB is guaranteed to exist at that point.
- User opens reuse the `CloseContext` embedded in the CCB after freeing query-template strings whose storage overlaps the context union, then mark `CCB_FLAG_CLOSE_CONTEXT`.
- Close paths deliberately avoid allocation after deciding to queue a user close.

## Queue Mechanics

- `FatAcquireCloseMutex` / `FatReleaseCloseMutex` wrap `FatCloseQueueMutex` with APC-disabled assertions and unsafe fast-mutex operations.
- Async close queue:
  - Used for close work that could not acquire resources synchronously.
  - Always starts the worker when no close worker is active.
- Delayed close queue:
  - Used when cleanup marked an unreferenced object as delay-close eligible.
  - Starts the worker only when delayed closes exceed `FatMaxDelayedCloseCount` and no worker is active.
- `FatRemoveClose` supports two modes:
  - Global worker mode (`Vcb == NULL`): removes async closes first, then delayed closes only under pressure or shutdown; clears `AsyncCloseActive` when no work remains.
  - Per-volume rundown mode: removes async and delayed closes from a specified VCB, used when a volume is being drained.
- High-water flags `HighAsync` and `HighDelayed` are enabled above twice the delayed-close limit and disabled below the normal limit, allowing the worker to reuse a recently held VCB more aggressively under pressure.

## Worker Batching

- In global worker mode, `FatFspClose` may keep the current VCB resource held while it drains several closes from the same volume.
- It releases/reacquires the VCB after about 20 same-volume closes when there are shared or exclusive waiters, preventing excessive starvation.
- It drops the VCB before a close that may delete the volume, detected with `OpenFileCount <= 1`, because `FatCommonClose` may acquire global state and tear down the VCB.
- If shutdown begins mid-drain, any held VCB is released before continuing.

## Open-Type Behavior in `FatCommonClose`

- `UnopenedFileObject`
  - Returns success without acquiring close resources.

- `VirtualVolumeFile`
  - Decrements `Vcb->InternalOpenCount` and `Vcb->ResidualOpenCount`.

- `UserVolumeOpen`
  - Decrements `DirectAccessOpenCount`, `OpenFileCount`, and `ReadOnlyCount` when the CCB was read-only.
  - Deletes the CCB.

- `EaFile`
  - Decrements `InternalOpenCount` and `ResidualOpenCount`.

- `DirectoryFile`
  - Decrements the DCB directory-file open count and VCB internal open count.
  - Decrements residual open count for root DCB directory files.
  - If this is a recursive close, returns immediately after the count updates; otherwise it falls through into the user file/directory FCB cleanup logic.

- `UserDirectoryOpen` and `UserFileOpen`
  - If a childless DCB has only this open and has an internal directory stream object, uninitializes that stream cache map, clears `DirectoryFile`, and dereferences the stream file object before destroying the FCB.
  - Decrements `Fcb->OpenCount`, `Vcb->OpenFileCount`, and read-only count as needed.
  - Deletes the CCB.

## FCB/DCB Teardown

- After per-open close work, unreferenced normal FCBs are deleted when `OpenCount == 0`.
- Non-root DCBs are deleted when:
  - Their child queue is empty.
  - `OpenCount == 0`.
  - `DirectoryFileOpenCount == 0`.
- Deleting an FCB/DCB sets `VCB_STATE_FLAG_DELETED_FCB`.
- After deleting a child, the code walks parent DCBs upward:
  - Uninitializes and dereferences parent directory stream file objects when no longer needed.
  - Deletes parent DCBs that become fully unreferenced after the stream close.
  - Stops when the parent still has a directory-file close outstanding.

## VCB Lifetime and Dismount

- `FatCommonClose` acquires the VCB exclusively unless it cannot wait, in which case it returns `STATUS_PENDING`.
- If `VCB_STATE_FLAG_CREATE_IN_PROGRESS` is set and the FCB is not the EA FCB, the close is postponed to avoid destroying an FCB during supersede/overwrite create work.
- `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` prevents recursive close chains from reentering full top-of-close-chain behavior.
- The first non-recursive close adds a temporary `OpenFileCount` bias so the VCB cannot disappear until dismount checks complete.
- In the finalizer, a top-level caller that supplied `VcbDeleted`, with only the biased open remaining and a non-good VCB condition, drops the VCB, acquires the global lock before the VCB, removes the bias, and calls `FatCheckForDismount`.
- If the VCB was not deleted, the close-in-progress flag is cleared and the VCB is released.

## Dependencies and Interactions

- Relies on `cleanup.c` to have already removed share access, per-handle locks, notifications, and set `FCB_STATE_DELAY_CLOSE` when eligible.
- Uses FastFAT global state in `FatData`: async/delayed close lists, per-volume close lists, counts, pressure flags, shutdown state, close worker item, close queue mutex, and process identity.
- Coordinates with cache manager via `CcUninitializeCacheMap`.
- Coordinates with object manager through `ObDereferenceObject`, which can synchronously trigger recursive close behavior.
- Uses `FatDeleteCcb`, `FatDeleteFcb`, `FatCheckForDismount`, and FastFAT resource helpers from the shared driver internals.

## Important Invariants

- Close must be allocation-averse after the decision to defer a user close; user close contexts come from the CCB.
- Global close list and per-VCB close list entries must be inserted and removed together under `FatCloseQueueMutex`.
- VCB lock ordering matters during dismount: the code deliberately drops the VCB and reacquires global-before-VCB when dismount may happen.
- Recursive directory stream closes are expected and are controlled with `VCB_STATE_FLAG_CLOSE_IN_PROGRESS`.
- The temporary VCB open-count bias is required so dismount checks cannot race with VCB deletion while close is deciding whether to tear down the volume.

## Notable Risks

- Queue counter/list consistency is critical; any mismatch between global and per-VCB list removal would strand close contexts or corrupt queue state.
- Worker batching improves throughput but depends on correctly dropping the VCB before possible final volume teardown.
- The parent DCB upward deletion loop depends on side effects of `ObDereferenceObject`, including possible recursive close IRPs.
- Close-without-cleanup is unusual but explicitly handled for oplocks only; other cleanup responsibilities are still expected to have happened in normal I/O manager ordering.

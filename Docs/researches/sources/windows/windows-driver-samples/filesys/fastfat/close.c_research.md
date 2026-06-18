# File Research: sources/windows/windows-driver-samples/filesys/fastfat/close.c

## Purpose

`close.c` implements FastFAT handling for `IRP_MJ_CLOSE`, which runs when the final reference to a file object is deleted. Unlike cleanup, close tears down in-memory structures: CCBs, FCBs/DCBs, internal stream references, and possibly the VCB during dismount.

The file also implements FastFAT’s async and delayed close queues. This lets the FSD close path avoid blocking or expensive teardown in unsafe contexts, while still allowing deferred cleanup of unreferenced objects.

## Main Entry Points

### `FatFsdClose`

Lines 79-319 implement the FSD dispatch routine for `IRP_MJ_CLOSE`.

Main responsibilities:

1. Complete immediately for filesystem device object requests.
2. Enter filesystem context.
3. Determine top-level IRP state.
4. Decode the file object into `Vcb`, `Fcb`, `Ccb`, and `TypeOfOpen`.
5. Preserve read-only file-object state in the CCB via `CCB_FLAG_READ_ONLY`.
6. On Windows 8+, if close arrives without prior cleanup, clean oplock state with `FsRtlCheckOplockEx`.
7. Preallocate close context for metadata stream opens.
8. Call `FatCommonClose` unless the FCB is marked for delayed close.
9. Queue close work if common close returns `STATUS_PENDING` or delayed close is requested.
10. Complete the IRP with success.

The close IRP itself is completed even when actual object teardown is queued for later.

### `FatCloseWorker`

Lines 321-352 is the I/O work item shim. It enters filesystem context, calls `FatFspClose(Context)`, then exits filesystem context.

### `FatFspClose`

Lines 355-550 drains queued close contexts, optionally for a specific VCB.

It is the worker/FSP-side close processor and repeatedly removes close contexts using `FatRemoveClose`, then calls `FatCommonClose` with `Wait = TRUE`.

### `FatQueueClose`

Lines 553-622 enqueues a `CLOSE_CONTEXT` onto either:

- Global and per-VCB delayed close lists, or
- Global and per-VCB async close lists.

It starts the worker item when thresholds or active-state rules require it.

### `FatRemoveClose`

Lines 625-826 removes a queued close context from global or per-VCB queues. It prioritizes async closes, then delayed closes under threshold/shutdown rules, and has pressure logic to favor the previous VCB when queues grow too high.

### `FatCommonClose`

Lines 829-1279 performs actual in-memory close teardown.

It acquires the VCB resource, updates open counts, deletes CCBs and FCBs/DCBs when unreferenced, unwinds parent directory stream file objects, and may check for dismount.

## Close Dispatch Behavior

`FatFsdClose` first decodes the file object before creating any heap-backed close context. For read-only file objects, it records `CCB_FLAG_READ_ONLY` so common close can decrement `Vcb->ReadOnlyCount`.

The `Wait` decision is conservative:

- `Wait` is true only when this is a top-level IRP and the current process is not FastFAT’s own process.
- Otherwise, if `FatCommonClose` cannot acquire needed resources, it returns `STATUS_PENDING`, and the close is queued.

For user file or directory opens, if `FCB_STATE_DELAY_CLOSE` is set and shutdown has not started, `FatFsdClose` skips immediate `FatCommonClose` and queues the close as delayed work.

## Close Context Ownership

Close contexts have two storage modes:

- Metadata stream opens (`VirtualVolumeFile`, `DirectoryFile`, `EaFile`) allocate a `CLOSE_CONTEXT` from VCB-managed preallocated close context storage with `FatAllocateCloseContext`; `CloseContext->Free = TRUE`.
- User opens reuse `Ccb->CloseContext`; `CloseContext->Free = FALSE`, and `CCB_FLAG_CLOSE_CONTEXT` is set.

Before using the CCB union field as a close context, `FatFsdClose` calls `FatDeallocateCcbStrings` because query template string storage overlaps with close context fields.

This design avoids allocating memory in the close path for user objects.

## Close Queues

### Queue Types

`FatQueueClose` distinguishes:

- Delayed close: for unreferenced objects intentionally kept around for reuse/efficiency.
- Async close: for closes that could not complete synchronously, usually because locks/resources were unavailable or create/close coordination required deferral.

Both queue types maintain:

- A global list under `FatData`.
- A per-VCB list under the target VCB.

The shared `FatCloseQueueMutex` protects all close lists and counters. Helper macros assert APCs are disabled and use `ExAcquireFastMutexUnsafe` / `ExReleaseFastMutexUnsafe`.

### Worker Start Rules

For delayed closes:

- Increment `FatData.DelayedCloseCount`.
- Start the worker only if delayed close count exceeds `FatMaxDelayedCloseCount` and async close worker is inactive.

For async closes:

- Increment `FatData.AsyncCloseCount`.
- Start the worker whenever no async close worker is active.

### Removal Rules

`FatRemoveClose` prioritizes async close work over delayed close work.

When no specific VCB is requested:

1. Pop from global async close list if nonempty.
2. Else pop from global delayed close list only if delayed count exceeds half the maximum or shutdown has started.
3. Else mark async close worker inactive and return null.

When a specific VCB is requested:

1. Pop from VCB async close list.
2. Else pop from VCB delayed close list.
3. Else, if a last-VCB hint was supplied, fall back to any close.
4. Else return null.

When queue counts grow above twice the delayed close limit, `FatRemoveClose` enters high-pressure mode (`HighAsync` or `HighDelayed`) and may prefer the last VCB hint to amortize expensive VCB acquisitions.

## FSP Close Processing

`FatFspClose` can run globally or for one VCB.

When running globally, it sets top-level IRP to `FSRTL_FSP_TOP_LEVEL_IRP`. It tries to reuse an exclusive VCB acquisition across multiple close contexts for the same VCB. To avoid starving other users of the VCB resource, it periodically releases and reacquires after about 20 loops if waiters exist.

It also avoids holding a VCB across a close that may delete the volume. If `OpenFileCount <= 1`, it releases the VCB before calling `FatCommonClose` because the common close path may tear the VCB down.

Each queued context is closed inside exception handling; expected exceptions are ignored. Pool-backed close contexts are freed after processing.

## Common Close Flow

`FatCommonClose` handles actual teardown and always starts by constructing a stack `IRP_CONTEXT` for close.

Early exits:

- `UnopenedFileObject` returns success.
- If exclusive VCB acquisition fails with `Wait == FALSE`, returns `STATUS_PENDING`.
- If create is in progress and this is not the EA FCB, releases VCB and returns `STATUS_PENDING`.

The routine uses `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` to detect recursive closes. The top close chain biases `Vcb->OpenFileCount` by one so the VCB cannot disappear before final dismount checks.

## Per-Open-Type Behavior

### `VirtualVolumeFile`

Decrements:

- `Vcb->InternalOpenCount`
- `Vcb->ResidualOpenCount`

Then returns success.

### `UserVolumeOpen`

Decrements:

- `Vcb->DirectAccessOpenCount`
- `Vcb->OpenFileCount`
- `Vcb->ReadOnlyCount` if CCB was marked read-only

Deletes the CCB with `FatDeleteCcb`.

### `EaFile`

Decrements:

- `Vcb->InternalOpenCount`
- `Vcb->ResidualOpenCount`

Then returns success.

### `DirectoryFile`

Decrements the directory file open count on the DCB and the VCB internal open count. If the FCB is the root DCB, also decrements residual open count.

If this is a recursive close, it returns success immediately. Otherwise it falls through to shared FCB/DCB deletion logic.

### `UserDirectoryOpen` and `UserFileOpen`

For DCBs, if the directory has no child DCBs, open count is one, and a stream directory file object exists, the code uninitializes that stream cache map, clears `DirectoryFile`, and dereferences the stream file object before destroying the FCB.

Then it decrements:

- `Fcb->OpenCount`
- `Vcb->OpenFileCount`
- `Vcb->ReadOnlyCount` if applicable

It deletes the CCB and proceeds to possible FCB/DCB deletion.

## FCB/DCB Deletion

After per-open-type work, `FatCommonClose` deletes in-memory file structures when no longer referenced.

Deletion conditions:

- For FCB: node type is `FAT_NTC_FCB` and `OpenCount == 0`.
- For DCB: node type is `FAT_NTC_DCB`, parent DCB queue is empty, `OpenCount == 0`, and `DirectoryFileOpenCount == 0`.

When deleting an FCB/DCB:

1. Save `ParentDcb`.
2. Set `VCB_STATE_FLAG_DELETED_FCB`.
3. Call `FatDeleteFcb`.

Then the routine may walk up parent directories. For each parent DCB that has no children, no opens, and a stream directory file object, it:

1. Uninitializes the parent stream cache map.
2. Clears `DirectoryFile`.
3. Dereferences the stream file object.
4. If the dereference caused final close of that directory file object, deletes the parent DCB and continues upward.
5. Otherwise stops and waits for memory manager/file object references to drain later.

This is the core recursive directory teardown logic.

## Dismount and VCB Lifetime

In the `finally` block, if this is the top of the close chain, the routine removes its biased open count and may check for dismount.

It can check for dismount only when:

- `Vcb->OpenFileCount == 1`, meaning only the bias remains.
- `Vcb->VcbCondition != VcbGood`.
- Dismount is not already in progress.
- Caller supplied `VcbDeleted`.
- Request is top level.

Because global lock order requires global before VCB, the code releases the VCB, sets wait mode, acquires global, reacquires VCB, removes the biased open count, and calls `FatCheckForDismount`.

If the VCB was deleted, it avoids releasing it. Otherwise it clears `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` and releases the VCB.

## Oplock Handling

On Windows 8+, `FatFsdClose` accounts for close IRPs that arrive without a prior cleanup. If the file object is not marked `FO_CLEANUP_COMPLETE` and the FCB is oplockable, it calls `FsRtlCheckOplockEx` to clear oplock state immediately. Comments state this is safe only in the FSD path and relies on the oplock package’s own lock rather than FCB locking.

Normal cleanup-time oplock coordination lives in `cleanup.c`; this is a fallback for abnormal close-without-cleanup cases.

## Concurrency and Locking

Important synchronization:

- `FatCloseQueueMutex` protects global/per-VCB close lists and counters.
- VCB resource is acquired exclusive in `FatCommonClose`.
- `VCB_STATE_FLAG_CLOSE_IN_PROGRESS` prevents recursive close handling from re-entering general teardown paths.
- FSP close worker may hold a VCB across several closes but periodically yields when waiters exist.
- Dismount path reacquires locks in global-before-VCB order.

The file is structured to avoid blocking in unsafe FSD close contexts by returning `STATUS_PENDING` and queueing.

## Error Handling

`FatFsdClose` wraps the close process with `FatExceptionFilter` and `FatProcessException`, though it generally completes the IRP after either synchronous or queued handling.

`FatFspClose` catches expected exceptions around `FatCommonClose` and ignores them, allowing the worker to continue draining close contexts.

`FatCommonClose` uses `try/finally` to guarantee biased open count cleanup, close-in-progress flag clearing, VCB release, and dismount handling.

## Key State Mutations

Important state touched:

- `FatData.AsyncCloseList`
- `FatData.DelayedCloseList`
- `FatData.AsyncCloseCount`
- `FatData.DelayedCloseCount`
- `FatData.AsyncCloseActive`
- `FatData.HighAsync`
- `FatData.HighDelayed`
- `FCB_STATE_DELAY_CLOSE`
- `CCB_FLAG_READ_ONLY`
- `CCB_FLAG_CLOSE_CONTEXT`
- `VCB_STATE_FLAG_CREATE_IN_PROGRESS`
- `VCB_STATE_FLAG_CLOSE_IN_PROGRESS`
- `VCB_STATE_FLAG_DELETED_FCB`
- `VCB_STATE_FLAG_DISMOUNT_IN_PROGRESS`
- `OpenFileCount`
- `OpenCount`
- `InternalOpenCount`
- `ResidualOpenCount`
- `DirectAccessOpenCount`
- `ReadOnlyCount`
- `DirectoryFileOpenCount`

## Relationship to `cleanup.c`

`cleanup.c` handles user-visible handle cleanup and may set `FCB_STATE_DELAY_CLOSE` when a final cleaned-up file or directory should remain cached briefly. `close.c` consumes that state and decides whether to defer actual FCB/DCB/CCB destruction.

The division is important:

- Cleanup removes share access, byte-range locks, cache maps for user file objects, delete-on-close names, and visible handle state.
- Close removes references and frees in-memory filesystem structures once the object is truly no longer referenced.

Together they model the Windows filesystem distinction between handle lifetime and file object lifetime.

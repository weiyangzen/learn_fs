# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/close.c

This file implements VFAT `IRP_MJ_CLOSE`, FCB release, and delayed-close worker support.

Key functions:
- `VfatCommonCloseFile`
  - No-ops for FAT metadata and volume FCBs.
  - If the last open handle is gone and cache remains initialized, uninitializes the cache map for the FCB’s stored file object, clears `FCB_CACHE_INITIALIZED`, and dereferences the file object.
  - Marks `FCB_CLOSED` in KDBG builds.
  - Releases the FCB, potentially deleting it.
- `VfatCloseWorker`
  - Processes global delayed-close list entries under `CloseMutex`.
  - Removes close contexts, decrements `CloseCount`, acquires the VCB directory resource, and closes FCBs still marked `FCB_DELAYED_CLOSE`.
  - Handles concurrent deletion by leaving context freeing to the other owner.
  - Clears `CloseWorkerRunning` when the list drains.
- `VfatPostCloseFile`
  - Allocates a close context from a paged lookaside list.
  - Stores VCB/FCB, links context to the FCB, inserts it into the global close list, increments `CloseCount`, and queues the close worker when more than 16 delayed closes accumulate and no worker is running.
- `VfatCloseFile`
  - Destroys the CCB if present.
  - If shutdown is active, delayed close is not requested, or delayed posting fails, closes immediately; otherwise leaves the FCB for delayed worker release.
  - Clears the file object’s filesystem contexts and section-object pointer.
  - Optionally checks dismount for volume closes under `ENABLE_SWAPOUT`.
- `VfatClose`
  - Returns success for the global filesystem device object.
  - Acquires the volume directory resource, calls `VfatCloseFile`, releases the resource, clears IRP information, and returns status. If the resource cannot be acquired in the current wait mode, it queues the IRP context.

Notable design points:
- The close path separates cleanup-time handle semantics from final object/FCB release.
- Delayed close is global and threshold-driven; it batches work until more than 16 entries are queued.
- Reopen logic in `create.c` can cancel delayed close and reuse the FCB before the worker processes it.

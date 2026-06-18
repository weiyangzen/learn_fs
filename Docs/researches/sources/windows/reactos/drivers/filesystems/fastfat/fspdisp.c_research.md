# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fspdisp.c

## Scope

This file implements the fastfat FSP worker-thread dispatcher. It receives a posted `IRP_CONTEXT`, forces waitable FSP execution, dispatches to the common routines for each major IRP function, handles exceptions consistently with FSD dispatchers, completes create IRPs in the worker when appropriate, and drains per-volume overflow work queued behind the current posted request.

## Public And Internal APIs Covered

- `FatFspDispatch()` is the FSP worker entry point.
- `FatRemoveOverflowEntry()` is a spin-lock protected helper that pops one queued overflow work item or decrements the posted-request count when no overflow work remains.

## Control Flow And Behavior

- `FatFspDispatch()` starts from the posted `IRP_CONTEXT`, original IRP, and current stack location. It sets `IRP_CONTEXT_FLAG_WAIT` and `IRP_CONTEXT_FLAG_IN_FSP` because worker processing may block.
- If the IRP has a file object, it derives the containing `VOLUME_DEVICE_OBJECT` from the stack device object so it can later inspect that volume's overflow queue.
- The dispatch loop enters filesystem context, sets top-level IRP state to either `FSRTL_FSP_TOP_LEVEL_IRP` for recursive calls or the current IRP, then switches on `IrpContext->MajorFunction`.
- Major functions are delegated to the matching common routine: create, close, read, write, query/set information, query/set EA, flush, query/set volume info, cleanup, directory control, filesystem control, lock control, device control, shutdown, and PNP. Unknown major functions are completed with `STATUS_INVALID_DEVICE_REQUEST`.
- Close is special: it decodes the file object, calls `FatCommonClose()` in async-close mode, completes the IRP, and clears the local `VolDo` if the close deleted the VCB so later overflow processing does not touch freed volume state.
- Exceptions are passed through `FatExceptionFilter()` and `FatProcessException()`, with a flag recording that the exception path already completed the IRP.
- Create requests are completed after leaving filesystem context when they did not pend and were not already completed by exception processing.
- After each request, if a valid volume device object remains, `FatRemoveOverflowEntry()` is called. A returned entry is converted back to `IRP_CONTEXT` via `WorkQueueItem.List`, wait/FSP flags are set, and the loop continues on that new IRP. If no entry exists, or if no volume object is available, the worker exits.
- `FatRemoveOverflowEntry()` acquires `OverflowQueueSpinLock`, removes the head entry when `OverflowQueueCount` is positive, decrements that count, and otherwise decrements `PostedRequestCount` to account for the worker thread going idle.

## State And Data Structures

- Request state: `IRP_CONTEXT`, original IRP, current stack location, major function, recursive-call flag, wait/FSP flags, and top-level IRP TLS.
- Volume queue state: `VOLUME_DEVICE_OBJECT::OverflowQueue`, `OverflowQueueCount`, `PostedRequestCount`, and `OverflowQueueSpinLock`.
- Close path state: decoded `VCB`, `FCB`, `CCB`, `TYPE_OF_OPEN`, and `VcbDeleted` output from `FatCommonClose()`.

## Dependencies

- Calls the fastfat common routines implemented throughout the driver, including `FatCommonFileSystemControl()` from `fsctrl.c` and `FatCommonLockControl()` from `lockctrl.c`.
- Uses NT/FsRtl filesystem entry/exit and top-level IRP conventions.
- Uses kernel list and spin-lock primitives for overflow queue management.
- Relies on exception-handling helpers shared by the fastfat FSD/FSP paths.

## Risks And Invariants

- FSP processing always sets waitable context; common routines may assume blocking is legal after posting.
- Top-level IRP state must be cleared after each request to avoid contaminating later work on the same worker thread.
- The overflow queue is per-volume. The dispatcher must stop using `VolDo` if close deleted the VCB.
- `PostedRequestCount` is decremented only when a worker finds no overflow entry, representing one less active posted worker for the volume.

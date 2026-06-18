# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fspdisp.c

## Purpose

`fspdisp.c` implements the FastFAT FSP worker dispatch loop. Posted IRPs enter here when the FSD path cannot complete synchronously or when work is deliberately deferred to the filesystem process context.

## Main Routines

- `FatFspDispatch`
  - Receives an initial `IRP_CONTEXT` as worker-thread context.
  - Forces `IRP_CONTEXT_FLAG_WAIT` and `IRP_CONTEXT_FLAG_IN_FSP`.
  - Determines the volume device object when the IRP has a file object.
  - Enters filesystem context, sets the top-level IRP marker, and dispatches by major function.
  - Calls the corresponding common routine for create, close, read, write, query/set information, EA query/set, flush, volume query/set, cleanup, directory control, file-system control, lock control, device control, shutdown, and PNP.
  - Uses FastFAT exception filtering/processing to complete faulted IRPs.
  - Completes create IRPs after `FatCommonCreate` returns non-pending because create completion is centralized here.
  - After each IRP, checks the volume overflow queue and loops to process another queued IRP context before returning to the worker infrastructure.

- `FatRemoveOverflowEntry`
  - Spinlock-protected helper for a volume’s overflow queue.
  - If overflow work exists, decrements `OverflowQueueCount` and removes the head entry.
  - If no overflow work remains, decrements `PostedRequestCount` and returns `NULL`.

## Dispatch Coverage

The switch covers the main FastFAT IRP surface:

- `IRP_MJ_CREATE` -> `FatCommonCreate`
- `IRP_MJ_CLOSE` -> `FatCommonClose`
- `IRP_MJ_READ` -> `FatCommonRead`
- `IRP_MJ_WRITE` -> `FatCommonWrite`
- `IRP_MJ_QUERY_INFORMATION` / `SET_INFORMATION`
- `IRP_MJ_QUERY_EA` / `SET_EA`
- `IRP_MJ_FLUSH_BUFFERS`
- `IRP_MJ_QUERY_VOLUME_INFORMATION` / `SET_VOLUME_INFORMATION`
- `IRP_MJ_CLEANUP`
- `IRP_MJ_DIRECTORY_CONTROL`
- `IRP_MJ_FILE_SYSTEM_CONTROL`
- `IRP_MJ_LOCK_CONTROL`
- `IRP_MJ_DEVICE_CONTROL`
- `IRP_MJ_SHUTDOWN`
- `IRP_MJ_PNP`

Unknown major functions are completed with `STATUS_INVALID_DEVICE_REQUEST`.

## Integration Points

This file is the bridge between posted work items and the rest of FastFAT’s `FatCommon*` operation implementations. It relies on the IRP context carrying the original IRP, major/minor function, and queue linkage. It also coordinates with the per-volume overflow queue in `VOLUME_DEVICE_OBJECT`.

## Risk Notes

- Close processing can delete the VCB; the code nulls `VolDo` when that happens to avoid accessing the overflow queue through freed volume state.
- Exception handling can complete the IRP; the create completion path tracks this with `ExceptionCompletedIrp`.
- Overflow queue counters are protected only inside `FatRemoveOverflowEntry`; callers must preserve that locking discipline.

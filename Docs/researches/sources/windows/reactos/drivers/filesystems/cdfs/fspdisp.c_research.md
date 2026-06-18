# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fspdisp.c

## Purpose

`fspdisp.c` implements the CDFS filesystem process worker dispatch routine. Posted IRP contexts enter `CdFspDispatch`, which runs them in a filesystem worker context and dispatches by major IRP function.

## Main Function

`CdFspDispatch` receives an `IRP_CONTEXT` as `Context`, extracts its IRP and stack location, optionally derives the `VOLUME_DEVICE_OBJECT`, and enters a processing loop.

For each request it:

1. Marks the IRP context with FSP flags.
2. Enters the filesystem with `FsRtlEnterFileSystem`.
3. Sets thread context with `CdSetThreadContext`.
4. Runs the major-function switch inside SEH.
5. Handles exceptions through `CdExceptionFilter` and `CdProcessException`.
6. Retries if the status is `STATUS_CANT_WAIT` after cleaning the IRP context for more processing.
7. Exits the filesystem.
8. Services the volume overflow queue if present.

## IRP Major Functions Dispatched

The worker dispatches:

- `IRP_MJ_CREATE` -> `CdCommonCreate`
- `IRP_MJ_READ` -> `CdCommonRead`
- `IRP_MJ_QUERY_INFORMATION` -> `CdCommonQueryInfo`
- `IRP_MJ_SET_INFORMATION` -> `CdCommonSetInfo`
- `IRP_MJ_QUERY_VOLUME_INFORMATION` -> `CdCommonQueryVolInfo`
- `IRP_MJ_DIRECTORY_CONTROL` -> `CdCommonDirControl`
- `IRP_MJ_FILE_SYSTEM_CONTROL` -> `CdCommonFsControl`
- `IRP_MJ_DEVICE_CONTROL` -> `CdCommonDevControl`
- `IRP_MJ_LOCK_CONTROL` -> `CdCommonLockControl`
- `IRP_MJ_CLEANUP` -> `CdCommonCleanup`
- `IRP_MJ_PNP` -> asserts false, then calls `CdCommonPnp`
- defaults -> completes `STATUS_INVALID_DEVICE_REQUEST`

`IRP_MJ_CLOSE` asserts false, indicating close should not normally be handled through this FSP dispatch path.

## Overflow Queue Handling

After each request, if a volume device object was associated with the original file object, the routine checks `VolDo->OverflowQueue` under `OverflowQueueSpinLock`. If queued work exists, it decrements the overflow count, removes the next IRP context, updates `Irp` and `IrpSp`, and continues processing in the same worker invocation. If no queued work remains, it decrements `PostedRequestCount` and returns to the executive worker thread.

## Error Handling

The dispatch loop uses SEH around the common routine call. `STATUS_CANT_WAIT` triggers a retry path where `IRP_CONTEXT_FLAG_MORE_PROCESSING` is set and `CdCleanupIrpContext` prepares the context for another attempt.

## Dependencies

This file depends on all common IRP handlers, exception-processing helpers, CDFS thread context helpers, and volume overflow queue fields.

## Research Notes

This is a compact but central asynchronous dispatch bridge. It keeps worker-thread entry, retry-on-cannot-wait behavior, and per-volume overflow queue draining in one place.

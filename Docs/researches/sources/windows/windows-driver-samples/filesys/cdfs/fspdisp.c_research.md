# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fspdisp.c

## Purpose

Implements the CDFS FSP worker-thread dispatcher. Posted IRP contexts enter here and are routed to the common worker for their major function.

## Main Entry Point

- `CdFspDispatch`

## Key Behavior

`CdFspDispatch` receives an `IRP_CONTEXT`, extracts the IRP and current stack location, and identifies the associated `VOLUME_DEVICE_OBJECT` when the request has a file object. It then enters a processing loop.

For each IRP context it:

- sets `IRP_CONTEXT_FSP_FLAGS`
- enters the filesystem critical region
- sets CDFS thread context
- initializes exception status and IRP status/information
- dispatches by major function
- handles exceptions through `CdExceptionFilter` and `CdProcessException`
- retries internally on `STATUS_CANT_WAIT`
- exits the filesystem critical region

Supported dispatch targets include:

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
- `IRP_MJ_PNP` -> assertion plus `CdCommonPnp`
- default -> complete with `STATUS_INVALID_DEVICE_REQUEST`

`IRP_MJ_CLOSE` asserts false; close processing is not expected through this FSP dispatch path.

## Retry and Overflow Queue Handling

When processing returns `STATUS_CANT_WAIT`, the dispatcher marks `IRP_CONTEXT_FLAG_MORE_PROCESSING`, cleans the IRP context for retry, and runs the request again.

After a request finishes, if there is an associated volume device object, it checks the volume overflow queue under `OverflowQueueSpinLock`. If queued work exists, it decrements `OverflowQueueCount`, dequeues the next IRP context, and continues processing it in the same worker thread. If no overflow work remains, it decrements `PostedRequestCount` and returns to the executive worker thread.

## Dependencies

This file is the bridge from posted asynchronous work to the common CDFS request routines. It relies on IRP context flags, CDFS exception handling, thread-context setup, completion helpers, and the volume overflow queue fields initialized during mount.

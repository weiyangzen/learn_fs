# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/dispatch.c

This file is the central IRP dispatch and async work-queue bridge for Ext2Fsd. It builds IRP contexts, enters file-system critical regions, handles top-level IRP state, queues requests that must run later, and maps major IRP functions to the driver's operation-specific handlers.

Key responsibilities:
- Build and dispatch an `EXT2_IRP_CONTEXT` for each incoming IRP.
- Queue requests to a system work queue when the operation needs waitable context.
- Lock user buffers before pending queued requests.
- Resume operations after oplock completion.
- Wrap dispatch in structured exception handling.

Important functions:
- `Ext2OplockComplete`: Requeues the IRP context after successful oplock completion or completes it with the IRP error status.
- `Ext2LockIrp`: Locks user buffers for buffered read/write, query-directory, query/set EA, and selected filesystem-control output buffers before marking the IRP pending.
- `Ext2QueueRequest`: Sets wait/requeued flags, locks the IRP buffer, initializes the work item, queues it to `CriticalWorkQueue`, and returns `STATUS_PENDING`.
- `Ext2DeQueueRequest`: Worker callback that enters the file system, sets top-level IRP if needed, dispatches the request, and routes exceptions to Ext2Fsd handlers.
- `Ext2DispatchRequest`: Major-function switch for create, close, read, write, flush, file information, volume information, directory control, filesystem control, device control, locking, cleanup, shutdown, EA, and PnP.
- `Ext2BuildRequest`: Driver dispatch entry point; records passive-level/top-level state, allocates an IRP context, dispatches it, and restores thread state.

Important interactions:
- Routes directory control to `Ext2DirectoryControl`, device control to `Ext2DeviceControl`, and EA operations to `Ext2QueryEa`/`Ext2SetEa`.
- Uses `Ext2ExceptionFilter` and `Ext2ExceptionHandler` from `except.c` around both direct and queued dispatch.
- Uses `Ext2LockUserBuffer` so deferred work can safely access caller buffers.

Notable behavior and risks:
- `Ext2LockIrp` uses write parameters for both read and write lengths, relying on layout compatibility in the IRP stack.
- Query-directory and EA stack access uses `PEXTENDED_IO_STACK_LOCATION`, matching the driver's compatibility layer.
- Queued work runs in `CriticalWorkQueue`, so long-running filesystem operations can contend with other critical work items.

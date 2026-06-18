# File Research: sources/windows/reactos/drivers/filesystems/npfs/cleanup.c

This file implements cleanup IRP handling for the ReactOS Named Pipe FileSystem.

`NpCommonCleanup` obtains the current IRP stack location, initializes a deferred IRP list, acquires the NPFS VCB exclusively, and decodes the file object with `NpDecodeFileObject`. If the decoded object is a CCB, cleanup performs endpoint-specific state updates:
- For the server end, it asserts `ServerOpenCount` is nonzero and decrements it.
- It calls `NpSetClosingPipeState` with the CCB, IRP, named-pipe end, and deferred list so pipe state transitions and blocked waiters can be handled consistently.

After releasing the VCB, it completes deferred IRPs through `NpCompleteDeferredIrps` and returns `STATUS_SUCCESS`.

`NpFsdCleanup` is the FSD entry wrapper. It enters filesystem context with `FsRtlEnterFileSystem`, calls `NpCommonCleanup`, exits with `FsRtlExitFileSystem`, and completes the IRP unless the common path returned `STATUS_PENDING`. Completion stores the status in `Irp->IoStatus.Status` and uses `IO_NAMED_PIPE_INCREMENT`.

The key behavior is that cleanup closes pipe state and wakes deferred operations, but does not free the CCB itself. Object destruction is handled by close processing.

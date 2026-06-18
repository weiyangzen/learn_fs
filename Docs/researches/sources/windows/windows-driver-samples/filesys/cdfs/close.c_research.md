# File Research: sources/windows/windows-driver-samples/filesys/cdfs/close.c

CDFS close handling for FSD/FSP dispatch, including immediate, async, and delayed close processing.

Key responsibilities:
- Implements `CdCommonClose`, the FSD close entry point.
- Implements `CdFspClose`, the worker-side queue drain routine.
- Maintains async and delayed close queues through `CdQueueClose` and `CdRemoveClose`.
- Deletes CCBs once file objects are decoded.
- Decrements FCB/user references and calls teardown logic through `CdCommonClosePrivate`.
- Starts the close work item when async work exists or delayed-close thresholds need reduction.
- Coordinates possible VCB teardown/dismount after the last cleanup/user references disappear.

Important behavior:
- Closes always complete and return `STATUS_SUCCESS` to the I/O manager once CDFS has captured the needed FCB/reference data.
- Delayed close is used for last references to user files/directories on mounted volumes, preserving recently used FCBs up to `CdData` thresholds.
- Async close is used when resources cannot be acquired without violating close recursion/locking constraints.
- Delayed close stores a compact `IRP_CONTEXT_LITE`; async close reuses the original `IRP_CONTEXT` with the FCB and user-reference count packed into existing fields.
- `CdFspClose(Vcb)` drains all close items for a specific volume; `CdFspClose(NULL)` drains async work first and then delayed work only while reduction is active.
- VCB teardown checks are deliberately repeated under `CdData` synchronization because initial condition checks are unsafe but cheap.

Dependencies:
- Depends on CDFS object decoding, CCB allocation/free, VCB/FCB resources, reference accounting, teardown, dismount checks, `CdData` global close queues, and the filesystem work item `CdData.CloseItem`.
- Uses Windows filesystem entry/exit bracketing via `FsRtlEnterFileSystem` and `FsRtlExitFileSystem`.

Notable risks:
- The async queue encodes close state in `IrpContext->Irp` and `IrpContext->ExceptionStatus`, which is compact but easy to misuse.
- The delayed-close mechanism intentionally keeps FCB references alive, so volume dismount can be deferred until queue draining catches up.
- Correct lock ordering is central: the file comments explicitly call out recursive close and potential VCB/FCB acquisition-order issues.

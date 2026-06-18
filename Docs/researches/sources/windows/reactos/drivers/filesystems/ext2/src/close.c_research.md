# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/close.c

This file implements final `IRP_MJ_CLOSE` handling and delayed close work-queue dispatch.

Functions:
- `Ext2Close(PEXT2_IRP_CONTEXT IrpContext)`: releases CCBs and decrements VCB/FCB references after cleanup has already run. Handles filesystem device closes, volume-close CCB release, file-close CCB release, fast-I/O disabling, FCB drop timestamp updates, and deferred FCB dereference.
- `Ext2QueueCloseRequest(PEXT2_IRP_CONTEXT IrpContext)`: converts a normal close context into a delayed-close context, optionally sleeps if already delayed/file busy, initializes a work item, and queues it to `DelayedWorkQueue`.
- `Ext2DeQueueCloseRequest(PVOID Context)`: work item entry that enters the filesystem, invokes `Ext2Close`, and routes exceptions through the ext2 exception filter/handler.

Research notes:
- Comments explicitly warn against taking the VCB resource in the normal file close path because cache purging from cleanup can cause recursive close IRPs and reverse lock order.
- If resource acquisition fails, close is queued rather than blocking in the dispatch path.
- `FcbDerefDeferred` avoids calling `Ext2ReleaseFcb` while holding the FCB main resource.

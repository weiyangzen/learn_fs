# File Research: sources/windows/reactos/drivers/filesystems/npfs/close.c

This file implements close IRP handling for the ReactOS Named Pipe FileSystem.

`NpCommonClose` gets the current IRP stack location, initializes a deferred IRP list, acquires the NPFS VCB exclusively, and decodes the file object into FCB/CCB/end information. It handles two decoded node types:
- `NPFS_NTC_ROOT_DCB`: decrements the pipe FCB’s `CurrentInstances` count and deletes the CCB with `NpDeleteCcb`, passing the deferred list for any IRPs released by deletion.
- `NPFS_NTC_VCB`: decrements the global `NpVcb->ReferenceCount`.

It then releases the VCB, completes deferred IRPs, marks the close IRP successful, completes it with `IO_NAMED_PIPE_INCREMENT`, and returns `STATUS_SUCCESS`.

`NpFsdClose` is the filesystem-dispatch wrapper. It enters filesystem context, calls `NpCommonClose`, exits filesystem context, and returns the status. Unlike cleanup, the common close path always completes the IRP itself.

The file’s role is final reference teardown: cleanup transitions pipe state, while close releases per-open CCB/root references and VCB references.

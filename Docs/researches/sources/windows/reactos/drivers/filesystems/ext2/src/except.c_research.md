# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/except.c

This file centralizes structured exception filtering and recovery for Ext2Fsd IRP dispatch. It records exception status in the IRP context, distinguishes expected NTSTATUS exceptions from fatal bugs, handles verify/hard-error flows, and may requeue top-level operations that could not run in the current context.

Key responsibilities:
- Log exception records and context records for debugging.
- Validate the IRP context before using it.
- Convert expected exceptions into normal Ext2Fsd error handling.
- Bugcheck on unexpected exceptions without a valid IRP context.
- Complete, requeue, verify, or hard-error the active IRP as appropriate.

Important functions:
- `Ext2ExceptionFilter`: Prints diagnostic exception information, validates `EXT2_IRP_CONTEXT`, sets wait/exception fields, catches expected exceptions and dismounted-volume cases, or frees the context when continuing search.
- `Ext2ExceptionHandler`: Converts the saved exception code into IRP completion status, checks VCB validity and mount state, requeues top-level `STATUS_CANT_WAIT` or high-IRQL verify cases, handles user-induced errors, performs volume verification, and completes/frees the context.

Important interactions:
- Called by both direct dispatch in `Ext2BuildRequest` and queued dispatch in `Ext2DeQueueRequest`.
- Uses `IoVerifyVolume`, `IoRaiseHardError`, `IoSetHardErrorOrVerifyDevice`, `IoSetDeviceToVerify`, and `IoIsErrorUserInduced`.
- Calls `Ext2CheckDismount`, `Ext2NormalizeAndRaiseStatus`, `Ext2QueueRequest`, `Ext2CompleteIrpContext`, and `Ext2FreeIrpContext`.

Notable behavior and risks:
- The filter unconditionally calls `DbgBreak()` after printing exception details, which is intrusive in checked/debug scenarios.
- Verify-required handling may complete root creates with `STATUS_REPARSE` and `IO_REMOUNT`.
- Unexpected exceptions with no IRP context call `Ext2BugCheck`.
- The handler mutates `IrpContext->Flags` to wait mode during exception processing so recovery can block.

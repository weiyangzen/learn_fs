# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/lock.c

## Scope
Implements byte-range lock control dispatch for regular Ext2 files.

## Key Elements
- `Ext2LockControl()` validates that the request targets a mounted volume file object rather than the filesystem device.
- Rejects volume FCBs and directory files for lock control.
- Acquires the FCB main resource shared while processing the lock request.
- Calls `FsRtlCheckOplock()` before file-lock processing and leaves completion pending when oplock processing takes ownership.
- Calls `FsRtlProcessFileLock()` on `Fcb->FileLockAnchor`, letting FsRtl complete the IRP.
- Updates `Fcb->Header.IsFastIoPossible` after file-lock state changes.

## Dependencies
Depends on Ext2 IRP context/FCB structures, FsRtl oplock and file-lock packages, `Ext2OplockComplete()`, `Ext2IsFastIoPossible()`, and normal Ext2 IRP-context completion.

## Behavior/Risks
- The function sets `IrpContext->Irp = NULL` when FsRtl owns IRP completion, preventing double completion by Ext2.
- Directory locking is rejected with `STATUS_INVALID_PARAMETER`.
- If oplock handling returns anything other than success, Ext2 does not complete the context immediately because the oplock package may finish asynchronously.

# File Research: sources/windows/reactos/drivers/filesystems/fastfat/pnp.c

This file implements FastFAT Plug and Play dispatch for mounted volume device objects.

Key responsibilities:
- Dispatch `IRP_MJ_PNP` through `FatFsdPnp` and `FatCommonPnp`.
- Validate that the target device object is a FastFAT volume device with a VCB.
- Serialize PnP against teardown with the global resource.
- Handle query-remove, remove, surprise-remove, and cancel-remove minor functions.
- Pass unhandled PnP IRPs down to the storage stack.
- Coordinate volume locking, flushing, VPB reference protection, dismount initiation, and lower-driver completion waiting.

Important functions:
- `FatFsdPnp`: FSD wrapper that enters the filesystem, establishes top-level IRP state, creates an IRP context, and routes exceptions through `FatProcessException`.
- `FatCommonPnp`: forces wait semantics, finds the VCB from the device object, takes the global lock, validates object shape, and dispatches by minor function.
- `FatPnpAdjustVpbRefCount`: adjusts VPB reference counts under the VPB spin lock.
- `FatPnpQueryRemove`: locks the volume, flushes and cleans it, sends query-remove down synchronously, then initiates forced dismount on success.
- `FatPnpRemove`: unlocks any volume lock, passes remove down, flushes/cleans without flushing, and forces dismount.
- `FatPnpSurpriseRemove`: passes surprise-remove down, cleans local state without flushing, and forces dismount.
- `FatPnpCancelRemove`: unlocks a previously query-locked volume and forwards the cancel-remove IRP.
- `FatPnpCompletionRoutine`: signals a caller event and returns `STATUS_MORE_PROCESSING_REQUIRED`.

Important interactions:
- Uses `FatAcquireExclusiveGlobal`, `FatAcquireExclusiveVcb`, `FatReleaseGlobal`, and `FatReleaseVcb` for teardown ordering.
- Uses `FatLockVolumeInternal` and `FatUnlockVolumeInternal` around query/cancel remove.
- Uses `FatFlushAndCleanVolume` before dismount where appropriate.
- Uses `FatCheckForDismount(..., TRUE)` to disconnect or delete the VCB.
- Synchronous lower-driver calls copy the current stack location, install `FatPnpCompletionRoutine`, call `IoCallDriver`, and wait if pending.

Notable behavior and risks:
- Query-remove temporarily increments the VPB reference count while resources are dropped and reacquired in the correct order.
- Remove and surprise-remove both continue local dismount processing even when the lower storage stack is already gone.
- Cancel-remove may arrive even if FAT did not see or complete the original query, so the unlock is intentionally benign.

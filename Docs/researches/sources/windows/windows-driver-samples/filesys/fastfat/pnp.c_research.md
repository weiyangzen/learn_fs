# File Research: sources/windows/windows-driver-samples/filesys/fastfat/pnp.c

## Purpose
Implements Plug and Play handling for mounted FAT volumes. It responds to query remove, remove, surprise remove, cancel remove, and passes unknown PnP minors to the lower storage stack.

## Main Entry Points
- `FatFsdPnp`: FSD dispatch routine for `IRP_MJ_PNP`.
- `FatCommonPnp`: validates the volume device object and dispatches by PnP minor function.
- `FatPnpQueryRemove`: handles `IRP_MN_QUERY_REMOVE_DEVICE`.
- `FatPnpRemove`: handles `IRP_MN_REMOVE_DEVICE`.
- `FatPnpSurpriseRemove`: handles `IRP_MN_SURPRISE_REMOVAL`.
- `FatPnpCancelRemove`: handles `IRP_MN_CANCEL_REMOVE_DEVICE`.
- `FatPnpAdjustVpbRefCount`: adjusts VPB reference count under VPB spin lock.
- `FatPnpCompletionRoutine`: signals synchronous waiters and returns `STATUS_MORE_PROCESSING_REQUIRED`.

## Behavior
`FatFsdPnp` sets up filesystem entry, top-level IRP state, and an IRP context. PnP normally lacks a file object, so it usually forces waitable processing.

`FatCommonPnp` forces `IRP_CONTEXT_FLAG_WAIT`, acquires the global FAT resource exclusively, validates that the device object is a FastFAT volume device object with a valid VCB node type, and dispatches based on the minor function. Unknown minor functions release the global resource, skip the current stack location, call the lower device, and delete the IRP context without completing the IRP locally.

`FatPnpQueryRemove` locks the volume, temporarily bumps the VPB reference count while dropping and reacquiring locks in the required order, flushes and cleans the volume, sends the query down synchronously, and if lower drivers succeed initiates forced dismount through `FatCheckForDismount`.

`FatPnpRemove` unlocks the volume if necessary, forwards the remove IRP synchronously, flushes/cleans without flushing storage (`NoFlush`), then attempts forced dismount. This can be the first notification after some storage-stack failure paths.

`FatPnpSurpriseRemove` forwards the surprise removal synchronously, cleans what it can without flushing, and initiates dismount. It assumes the physical device may already be gone.

`FatPnpCancelRemove` reacquires the VCB, releases the global resource, unlocks the volume benignly, and passes the cancel IRP down without installing a completion routine because FAT does not need to observe completion.

## Synchronization
- Global resource protects against volume teardown while locating and validating the VCB.
- Query/remove/surprise paths acquire the VCB exclusively.
- Query remove deliberately releases and reacquires global/VCB resources to maintain lock ordering.
- VPB reference count changes are protected by `IoAcquireVpbSpinLock`.
- Forwarded PnP IRPs that FAT must observe are sent with a completion routine and waited on via `KEVENT`.

## Dependencies
- `FatAcquireExclusiveGlobal`
- `FatAcquireExclusiveVcb`
- `FatLockVolumeInternal`
- `FatUnlockVolumeInternal`
- `FatFlushAndCleanVolume`
- `FatCheckForDismount`
- `IoCallDriver`
- `IoCopyCurrentIrpStackLocationToNext`
- `IoSkipCurrentIrpStackLocation`
- `IoSetCompletionRoutine`

## Important Notes
The file is primarily about safe teardown ordering. Query remove is the strongest path: FAT locks, flushes, passes the query down, and then tries to dismount immediately. Surprise and remove paths avoid relying on successful media access and use `NoFlush`.

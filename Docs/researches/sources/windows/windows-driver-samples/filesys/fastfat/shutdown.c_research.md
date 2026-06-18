# File Research: sources/windows/windows-driver-samples/filesys/fastfat/shutdown.c

## Purpose
Implements FastFAT filesystem shutdown. It flushes mounted volumes, marks clean volumes clean, sends shutdown IRPs to lower storage devices, dismounts where possible, unregisters filesystem device objects, and completes the shutdown IRP.

## Main Entry Points
- `FatFsdShutdown`: dispatch routine for `IRP_MJ_SHUTDOWN`.
- `FatCommonShutdown`: common shutdown implementation.

## Behavior
`FatFsdShutdown` enters the filesystem, establishes top-level IRP state, creates a waitable IRP context, and calls `FatCommonShutdown`. Exceptions are handled through FAT’s normal exception path.

`FatCommonShutdown` disables popups and forces write-through behavior on the IRP context. It sets `FatData.ShutdownStarted`, acquires the global FAT resource exclusively, then iterates all VCBs on `FatData.VcbQueue`.

For each mounted, good, not-yet-shutdown volume:
- Acquires the volume exclusively.
- Attempts to flush the volume.
- If the mounted-dirty flag is not set, purges the volume file cache section and marks the volume clean.
- Builds and sends a synchronous `IRP_MJ_SHUTDOWN` to the target device object.
- Marks the VCB with `VCB_STATE_FLAG_SHUTDOWN`.
- Calls `FatCheckForDismount`.
- Releases the volume if the VCB was not deleted.

Exceptions during flush or lower-device shutdown are caught locally, reset in the IRP context, and do not prevent sending shutdown to the target device or processing subsequent volumes.

The final block releases the global resource, unregisters disk and CD-ROM filesystem device objects, deletes those device objects, and completes the original IRP with `STATUS_SUCCESS`.

## Dependencies
- `FatAcquireExclusiveGlobal`
- `FatAcquireExclusiveVolume`
- `FatFlushVolume`
- `FatMarkVolume`
- `FatCheckForDismount`
- `IoBuildSynchronousFsdRequest`
- `IoCallDriver`
- `IoUnregisterFileSystem`
- `IoDeleteDevice`
- `CcPurgeCacheSection`

## Important Notes
Shutdown is deliberately synchronous and global. It favors best-effort cleanup: even if flushing a volume raises, the code still tries to notify the lower storage stack with shutdown so device caches can be flushed.

# File Research: sources/windows/reactos/drivers/filesystems/fastfat/shutdown.c

This file implements FastFAT filesystem shutdown handling.

Key responsibilities:
- Dispatch `IRP_MJ_SHUTDOWN` through `FatFsdShutdown`.
- Serialize shutdown with the global filesystem resource.
- Flush and clean every mounted FAT volume that has not already been shut down.
- Send shutdown IRPs to underlying target devices.
- Mark VCBs as shut down and try to dismount them.
- Unregister and delete the FastFAT disk and CD-ROM filesystem device objects.

Important functions:
- `FatFsdShutdown`: FSD wrapper that enters the filesystem, creates a waitable IRP context, calls `FatCommonShutdown`, and handles exceptions.
- `FatCommonShutdown`: core shutdown routine.

Shutdown flow:
1. Set `IRP_CONTEXT_FLAG_DISABLE_POPUPS` and `IRP_CONTEXT_FLAG_WRITE_THROUGH`.
2. Set `FatData.ShutdownStarted = TRUE`.
3. Acquire the global resource exclusively.
4. Iterate `FatData.VcbQueue`.
5. Skip already-shutdown or non-good VCBs.
6. Acquire each volume exclusively.
7. Flush the volume and mark it clean when not mounted dirty.
8. Build and send a synchronous `IRP_MJ_SHUTDOWN` to the target device.
9. Set `VCB_STATE_FLAG_SHUTDOWN`.
10. Call `FatCheckForDismount`.
11. Release the volume if it survived.
12. Release global, unregister filesystems, delete filesystem device objects, and complete the original IRP.

Notable behavior and risks:
- Flush exceptions are swallowed after resetting exception state, because the lower storage stack still needs shutdown notification.
- The volume file cache is purged before marking the volume clean to avoid stale BPB state.
- The routine unregisters and deletes global filesystem device objects from the shutdown path.

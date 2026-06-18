# File Research: sources/windows/winfsp/src/dll/mount.c

This file implements mount-point creation and removal for WinFsp volumes.

Key responsibilities:
- Initializes optional `ntdll` symbolic-link functions and registry-controlled mount behavior:
  - `MountDoNotUseLauncher`
  - `MountBroadcastDriveChange`
  - `MountUseMountmgrFromFSD`
- Supports Mount Manager drive and directory mount flows, either through user-mode Mount Manager calls or by delegating to the FSD depending on registry configuration.
- Supports DOS drive-letter mounts via `DefineDosDeviceW`; when in a non-LocalSystem service context, can ask the launcher to define/remove global drive symlinks.
- Makes drive symbolic links temporary with `NtMakeTemporaryObject` when possible.
- Broadcasts device change notifications in a detached thread to avoid Explorer/shell hangs.
- Notifies shell on drive removal to clear stale navigation entries.
- Creates directory mount points by creating a directory handle with delete-on-close and setting an `IO_REPARSE_TAG_MOUNT_POINT` reparse buffer.
- Rejects directory mount points that point to network-style volume names, since Windows junctions cannot target network filesystems.
- `FspMountSet_Internal` handles automatic drive selection for `*:` and dispatches by mountpoint type.
- `FspMountSet` optionally sends an early `Transact0` workaround for drive mounts under `FSP_CFG_REJECT_EARLY_IRP`.
- `FspMountRemove` dispatches removal and sends shell cleanup notification for drives.

Filesystem relevance:
- This is the Windows namespace attachment layer for WinFsp volumes.
- It handles the difference between DOS drive symlinks, Mount Manager drive letters, Mount Manager directory mount points, and raw directory junction-style mount points.

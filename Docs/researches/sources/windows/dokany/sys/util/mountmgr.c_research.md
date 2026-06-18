# File Research: sources/windows/dokany/sys/util/mountmgr.c

Mount Manager integration helpers for Dokan volume arrival, mount point creation/deletion, delete-point requests, and AutoMount control.

Key responsibilities:
- Sends arbitrary IOCTLs to `\Device\MountPointManager`.
- Notifies Mount Manager about directory mount point creation/deletion for persistent symbolic links.
- Sends volume-arrival notifications for Dokan device names.
- Creates explicit mount points for device names.
- Deletes mount points by symbolic link, device name, or both.
- Queries and sets Mount Manager AutoMount state.
- Provides wrappers for directory mount point created/deleted notifications.

Important behavior:
- `DokanSendIoContlToMountManager` opens the mount manager device, builds a synchronous device-control IRP, waits if pending, uses `iosb.Status`, and dereferences the file object.
- Mount point notification packs `MOUNTMGR_VOLUME_MOUNT_POINT` with source mount point and target persistent symbolic link in a single allocated buffer.
- Volume arrival packs a `MOUNTMGR_TARGET_NAME` with the Dokan device name.
- Delete-points packs optional symbolic link and optional device name into `MOUNTMGR_MOUNT_POINT`, and allocates a small output buffer for deleted points.
- Create-point logs success/failure to the Windows Event Log using `DokanLogInfo`/`DokanLogError`.
- The file comments warn that deleting by drive-letter mount point without a device name can create a Mount Manager database record suppressing future auto-assignment for that drive letter.

Dependencies:
- Includes `mountmgr.h`, which includes Dokan core types and `<mountmgr.h>`.
- Uses Mount Manager IOCTL structures and constants.
- Uses Dokan allocation/logging helpers and Windows I/O routines: `IoGetDeviceObjectPointer`, `IoBuildDeviceIoControlRequest`, `IoCallDriver`, `KeWaitForSingleObject`, and `ObDereferenceObject`.

Notable risks:
- `DokanSendIoContlToMountManager` returns early on `IoBuildDeviceIoControlRequest` failure without dereferencing `mountFileObject`, which is a potential leak on that error path.
- Packing Mount Manager variable-length structures depends on exact byte lengths and offsets.
- The function name `DokanSendIoContlToMountManager` appears to contain a typo, but the declaration and implementation match.

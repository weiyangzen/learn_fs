# File Research: sources/windows/winbtrfs/src/devctrl.c

## Scope

This file implements WinBtrfs `IRP_MJ_DEVICE_CONTROL` dispatch for filesystem device objects, the control device object, and volume device objects. It handles a small set of WinBtrfs-private IOCTLs, two filesystem-device IOCTLs, and passes unhandled filesystem-device controls to the underlying real device.

## Entry Points And Major APIs

- `mountdev_query_stable_guid(Vcb, Irp)`: handles `IOCTL_MOUNTDEV_QUERY_STABLE_GUID` by returning the mounted filesystem UUID as a stable mount manager GUID.
- `is_writable(Vcb)`: handles `IOCTL_DISK_IS_WRITABLE`, returning `STATUS_MEDIA_WRITE_PROTECTED` when the volume is mounted readonly.
- `query_filesystems(data, length)`: handles `IOCTL_BTRFS_QUERY_FILESYSTEMS` on the control device by enumerating loaded VCBs and their devices into a `btrfs_filesystem` / `btrfs_filesystem_device` variable-length buffer.
- `probe_volume(data, length, processor_mode)`: handles `IOCTL_BTRFS_PROBE_VOLUME` by validating a `MOUNTDEV_NAME`, requiring manage-volume privilege, opening the target device, refreshing disk properties when appropriate, and re-running WinBtrfs arrival/removal probing.
- `ioctl_unload(Irp)`: handles `IOCTL_BTRFS_UNLOAD`, requiring load-driver privilege and then invoking `do_shutdown`.
- `control_ioctl(Irp)`: dispatches WinBtrfs-private control-device IOCTLs.
- `drv_device_control(DeviceObject, Irp)`: exported `IRP_MJ_DEVICE_CONTROL` dispatch routine.

## Core Control Flow

`drv_device_control` enters the filesystem, marks top-level IRP state, clears `IoStatus.Information`, and dispatches according to the device extension type. Control-device requests go to `control_ioctl`. Volume-device requests are delegated to `vol_device_control`. Non-filesystem/non-volume device extension types are rejected.

For filesystem VCBs, it directly handles `IOCTL_MOUNTDEV_QUERY_STABLE_GUID` and `IOCTL_DISK_IS_WRITABLE`. Any other control code is passed down to `Vcb->Vpb->RealDevice` with `IoSkipCurrentIrpStackLocation` and `IoCallDriver`; in that pass-through path the function does not complete the IRP itself.

`query_filesystems` acquires `global_loading_lock` shared, walks `VcbList`, and for each mounted filesystem records the filesystem UUID and number of devices under `Vcb->tree_lock`. For each device it copies the device UUID and either queries `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME` from the underlying device object or marks the device missing. The output is a chained variable-size list using each entry's `next_entry` offset.

`probe_volume` validates caller buffer length, checks `SE_MANAGE_VOLUME_PRIVILEGE`, opens the named device with `IoGetDeviceObjectPointer`, gets the PnP interface name and class GUID, optionally issues `IOCTL_DISK_UPDATE_PROPERTIES` for disks, dereferences the file object, calls `volume_removal`, then calls either `disk_arrival` or `volume_arrival` to rescan the path.

## Important State Mutated

- `Irp->IoStatus.Information` is set for stable GUID responses and left at zero for most controls.
- `btrfs_filesystem` output records are populated from `VcbList`, each VCB's `superblock.uuid`, `superblock.num_devices`, and device UUID/name/missing state.
- Disk/volume probing can trigger global device-arrival/removal side effects through `volume_removal`, `disk_arrival`, and `volume_arrival`.
- `ioctl_unload` initiates driver shutdown through `do_shutdown`.

## Dependencies

This file uses Windows storage, mount manager, and security interfaces: `MOUNTDEV_STABLE_GUID`, `MOUNTDEV_NAME`, `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`, `IOCTL_DISK_IS_WRITABLE`, `IOCTL_DISK_UPDATE_PROPERTIES`, `GUID_DEVINTERFACE_DISK`, `IoGetDeviceObjectPointer`, object dereference, privilege checks, and IRP pass-through APIs. It also depends on project globals and helpers: `drvobj`, `VcbList`, `global_loading_lock`, `dev_ioctl`, `get_device_pnp_name`, `volume_removal`, `disk_arrival`, `volume_arrival`, `do_shutdown`, and `vol_device_control`.

## Notable Behaviors

- If no filesystems are mounted, `IOCTL_BTRFS_QUERY_FILESYSTEMS` returns a single zeroed `btrfs_filesystem` record when the buffer is large enough.
- Device names in `query_filesystems` are queried in two stages: first enough to learn/validate length behavior, then into the caller's variable-length output structure.
- The control-device IOCTL dispatcher uses `Parameters.FileSystemControl.*` buffer lengths for private IOCTLs even though the top-level routine is `IRP_MJ_DEVICE_CONTROL`.
- Filesystem-device control codes not recognized by WinBtrfs are transparently forwarded to the real underlying device.

## Risks And Edge Cases

- `query_filesystems` advances the output pointer and sets the previous `next_entry` before fully proving the remaining buffer can hold the next complete filesystem entry. It returns `STATUS_BUFFER_OVERFLOW` on shortage, but partial output may already be written.
- In `query_filesystems`, the second `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME` writes into `&bfd->name_length` with a buffer size covering `MOUNTDEV_NAME.Name[0] + NameLength`; this relies on the layout of `btrfs_filesystem_device` matching the mountdev name-length/name layout.
- `probe_volume` stores `guid` returned by `get_device_pnp_name` and continues using it after dereferencing the file object. This is safe only if that helper returns storage whose lifetime is independent of the file object.
- `drv_device_control` forwards unhandled controls to `Vcb->Vpb->RealDevice` without additional validation; correctness depends on `Vpb` and `RealDevice` being valid for mounted filesystem VCBs.

## Summary

`devctrl.c` is a compact IOCTL router. It exposes WinBtrfs control operations for filesystem enumeration, volume probing, and unload; answers mount/writability queries for mounted filesystems; delegates volume-device IOCTLs; and passes unknown filesystem-device controls to the underlying storage stack.

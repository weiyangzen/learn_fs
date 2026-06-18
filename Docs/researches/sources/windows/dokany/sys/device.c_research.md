# File Research: sources/windows/dokany/sys/device.c

## Role

Handles device and volume control requests for Dokan disk, volume, mount-manager, storage, and network redirector behavior.

## Main Functions

- `GlobalDeviceControl`
- `DokanPopulateDiskGeometry`
- `DokanPopulatePartitionInfo`
- `DokanPopulatePartitionInfoEx`
- `DiskDeviceControl`
- `DiskDeviceControlWithLock`
- `IsVolumeOpen`
- `DokanGetVolumeMetrics`
- `VolumeDeviceControl`
- `DokanDispatchDeviceControl`

## Behavior

Supports IOCTL families for:

- Disk geometry and length:
  - `IOCTL_DISK_GET_DRIVE_GEOMETRY`
  - `IOCTL_DISK_GET_LENGTH_INFO`
- Partition and layout information:
  - `IOCTL_DISK_GET_DRIVE_LAYOUT`
  - `IOCTL_DISK_GET_DRIVE_LAYOUT_EX`
  - `IOCTL_DISK_GET_PARTITION_INFO`
  - `IOCTL_DISK_GET_PARTITION_INFO_EX`
- Write protection:
  - `IOCTL_DISK_IS_WRITABLE`
  - `IOCTL_VOLUME_GET_GPT_ATTRIBUTES`
- Storage media/hotplug:
  - `IOCTL_STORAGE_GET_HOTPLUG_INFO`
  - `IOCTL_STORAGE_CHECK_VERIFY`
  - `IOCTL_STORAGE_GET_MEDIA_TYPES_EX`
  - `IOCTL_STORAGE_GET_DEVICE_NUMBER`
  - `IOCTL_STORAGE_QUERY_PROPERTY`
- Mount manager:
  - `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`
  - `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`
  - `IOCTL_MOUNTDEV_QUERY_SUGGESTED_LINK_NAME`
  - `IOCTL_MOUNTDEV_LINK_CREATED`
  - `IOCTL_MOUNTDEV_LINK_DELETED`
- Network redirector path checks:
  - `IOCTL_REDIR_QUERY_PATH`
  - `IOCTL_REDIR_QUERY_PATH_EX`
- Volume metrics:
  - `DokanGetVolumeMetrics`

## Dependencies

- `dokan.h`
- `util/irp_buffer_helper.h`
- `util/str.h`
- Windows headers:
  - `mountdev.h`
  - `mountmgr.h`
  - `ntddvol.h`
  - `storduid.h`

## Important Details

- Uses remove locks in `DiskDeviceControlWithLock`.
- Rejects requests for deleted or unmounted devices.
- Maintains actual mount point after mount-manager link creation.
- Can trigger unmount when a mount-manager link is externally deleted.
- Volume-level mountdev controls require opening the volume, not a normal file handle.
- UNC redirector handling validates path prefixes and reports accepted UNC length.

## Notes and Risks

- Many storage responses are synthetic defaults, not real disk layout data.
- Mount-manager behavior must stay synchronized with DCB global mount entries.
- Device deletion and unmount pending checks guard against use-after-removal paths.

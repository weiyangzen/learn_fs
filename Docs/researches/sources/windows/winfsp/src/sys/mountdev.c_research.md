# File Research: sources/windows/winfsp/src/sys/mountdev.c

## Purpose

`mountdev.c` implements Mount Manager support for WinFsp virtual volume devices. It lets an fsvrt device answer mountdev IOCTLs, provide a device name and unique ID, become persistent or nonpersistent, and purge nonpersistent mount manager points during teardown.

## Main Contents

- `FspMountdevQueryDeviceName`
- `FspMountdevQueryUniqueId`
- `FspMountdevDeviceControl`
- `FspMountdevMake`
- `FspMountdevFini`

## Control Flow

- `FspMountdevDeviceControl` handles mountdev IOCTLs only if the fsvrt extension has `IsMountdev` set.
- Supported IOCTLs:
  - `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`
  - `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`
- `FspMountdevMake`:
  - requires external concurrency protection, usually the mount mutex,
  - rejects repeated conversion unless persistence matches,
  - stores persistence mode,
  - creates a stable UUID v5 for persistent volumes from filesystem name, serial number, and creation time,
  - creates a random GUID for nonpersistent volumes,
  - copies the GUID to `UniqueId`,
  - marks the fsvrt device as mountdev-capable.
- `FspMountdevFini`:
  - returns immediately if the device was not a mountdev,
  - keeps Mount Manager state for persistent devices,
  - for nonpersistent devices, sends `IOCTL_MOUNTMGR_DELETE_POINTS` keyed by the mountdev unique ID.

## Buffer Handling

Both query routines first require the fixed header size, then set `IoStatus.Information` to the full required size. If the caller buffer cannot hold the variable-length payload, they return `STATUS_BUFFER_OVERFLOW` after reporting the fixed header size.

## Integration

This file relies on fsvrt and fsvol device extensions, `FspUuid5Make`, `FspCreateGuid`, and `FspSendMountmgrDeviceControlIrp` from utility code.

## Notable Details

- The query unique ID payload is the binary GUID stored in the fsvrt device extension.
- Persistent and nonpersistent mountdev conversion cannot be mixed after the device is marked.
- `FspMountdevFini` intentionally does not clear `IsMountdev`; it only cleans external Mount Manager state.

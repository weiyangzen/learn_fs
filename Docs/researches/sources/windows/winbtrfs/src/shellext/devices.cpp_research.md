# File Research: sources/windows/winbtrfs/src/shellext/devices.cpp

Read status: complete, 958 lines.

This file implements elevated device-management dialogs and rundll exports for adding, removing, and resizing devices in a Btrfs filesystem.

Main behavior:
- `find_devices` enumerates disks, volumes, and hidden volumes through SetupAPI device-interface GUIDs.
- It opens devices with NT APIs, collects length, disk/partition number, storage descriptor text, partition layout, mount points, and filesystem identity.
- Filesystem identity is detected by scanning superblock magic definitions from `fs_ident` in `devices.h`.
- Btrfs superblocks contribute filesystem UUID and device UUID for matching devices to mounted Btrfs filesystems.
- Btrfs pseudo-devices named like `\\Device\\Btrfs{...}` are ignored for add-device display.
- `BtrfsDeviceAdd::populate_device_tree` builds the device tree and groups partitions under disks when possible.
- Existing mounted Btrfs filesystems are queried via `IOCTL_BTRFS_QUERY_FILESYSTEMS` to identify multi-device state and drive letters.

Device operations:
- `BtrfsDeviceAdd::AddDevice` confirms destructive use of formatted devices, opens the selected raw device, optionally locks/dismounts/unlocks volumes, and calls `FSCTL_BTRFS_ADD_DEVICE`.
- `RemoveDeviceW` parses `volume|device_id`, enables `SeManageVolumePrivilege`, sends `FSCTL_BTRFS_REMOVE_DEVICE`, and launches a balance UI. It maps `STATUS_CANNOT_DELETE` to a RAID-specific message.
- `BtrfsDeviceResize::do_resize` sends `FSCTL_BTRFS_RESIZE`. If the driver returns `STATUS_MORE_PROCESSING_REQUIRED`, it opens the balance workflow for relocation.
- `ResizeDeviceW` parses `volume|device_id`, enables privilege, and shows the resize dialog.
- `AddDeviceW`, `RemoveDeviceW`, and `ResizeDeviceW` are exported C callbacks intended for elevated `rundll32.exe` invocation.

UI behavior:
- Uses themed dialogs, tree controls, and a slider for resize size in MiB units.
- Add-device OK is enabled only for valid targets: non-partitioned disks or volumes, excluding already multi-device Btrfs members.
- Resize dialog queries `FSCTL_BTRFS_GET_DEVICES` to find current and maximum size for the selected device.

Important dependencies and integration:
- Uses `mountmgr` wrapper from `mountmgr.cpp` to map device names to drive letters.
- Uses `BtrfsBalance` from `balance.h` for post-remove or post-resize relocation.
- Uses `../btrfs.h` and `../btrfsioctl.h` for superblock and ioctl structures.
- Uses shared `format_size`, `load_string`, `wstring_sprintf`, `error_message`, and privilege/error helpers from the shell extension support code.

Risk and maintenance notes:
- Raw device operations require `SeManageVolumePrivilege` and can be destructive. The confirmation for formatted devices is important.
- There appears to be a UUID comparison typo in device matching: it compares `device_list[i].dev_uuid` to itself rather than to the iterated `dev` UUID, so child-device matching may be too broad.
- `find_devices` returns early on the first `SetupDiEnumDeviceInterfaces` failure without destroying the device-info list in that branch.
- Several manual allocations and NT variable-size buffers require careful bounds handling.

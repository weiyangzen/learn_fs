# File Research: sources/windows/reactos/drivers/filesystems/btrfs/search.c

## Scope And Purpose

`search.c` handles Btrfs device discovery, arrival/removal notifications, encrypted-volume unlock callbacks, child volume teardown, drive-letter removal/restoration, and mount-manager monitoring. Despite the filename, this is not B-tree search logic; it is the driver’s Windows PnP and mount-manager discovery layer.

Complete file read: 1128 lines.

## Discovery And Ignore Handling

`fs_ignored` builds a registry path from the driver registry root plus the Btrfs filesystem UUID and reads a `REG_DWORD` value named `Ignore`. If set, the discovered filesystem is skipped. It allocates the UUID path dynamically, opens/creates the registry key with `ZwCreateKey`, queries the value with `ZwQueryValueKey`, and frees temporary allocations.

`test_vol` probes a `PDEVICE_OBJECT`/`PFILE_OBJECT` pair. It determines sector size, reads the primary Btrfs superblock, optionally scans backup superblocks and keeps the newest generation, verifies checksum and magic, checks the ignore registry setting, clears `DO_VERIFY_VOLUME`, and calls `add_volume_device`. If the read returns `STATUS_FVE_LOCKED_VOLUME`, it either requests retry behavior or registers a BitLocker/FVE unlock notification.

## FVE Callback Path

The file maintains `fve_data_list` under `fve_data_lock`.

- `register_fve_callback` stores the device path and registers a target-device-change notification for `GUID_IO_VOLUME_FVE_STATUS_CHANGE`.
- `event_notification` receives the FVE event, finds the stored device record, copies the path into a work-item context, and queues `fve_callback`.
- `fve_callback` retries `volume_arrival` with the callback flag set. If arrival succeeds, it unregisters the PnP notification and removes the stored record.

This defers volume probing out of the notification callback and avoids doing heavier mount logic directly in the callback context.

## Disk And Volume Arrival

`disk_arrival` handles disk-interface arrivals. It opens the device, rejects disks with partitions because partition arrivals will be considered separately, queries length and storage device number, and calls `test_vol`.

`volume_arrival` handles volume-interface arrivals. It opens the device under `boot_lock`, ignores devices created by this driver, sends `IOCTL_VOLUME_ONLINE`, queries length and storage device number, removes a whole-disk Btrfs child if a partition appears for the same disk, and then calls `test_vol`.

Both paths protect boot/discovery state with `boot_lock`.

## Removal And Child Teardown

`volume_removal` normalizes device paths with `\\?\`/`\??\` style prefixes, scans all PDOs and volume children, and removes matching non-boot children.

`remove_volume_child` is the central teardown routine. The caller must hold `pdode->child_lock` exclusively, and the function releases it before returning. It unregisters child notifications, triggers surprise removal unless degraded mode permits missing devices, disables the volume interface, restores drive letters to remaining children if appropriate, marks devices missing for degraded mounts, updates removable-media characteristics, drops object/path references, removes the child from lists, decrements `children_loaded`, and deletes the volume device when the last child disappears and no opens remain.

The function also invalidates bus relations when the PDO set changes.

## Mount Manager Coordination

`remove_drive_letter` asks mountmgr to delete mount points for a device name, using the standard two-call buffer-size pattern for `IOCTL_MOUNTMGR_DELETE_POINTS`.

`mountmgr_thread` opens `MOUNTMGR_DEVICE_NAME`, loops on `IOCTL_MOUNTMGR_CHANGE_NOTIFY`, queries current mount points on each change, and passes them to `mountmgr_updated`.

`mountmgr_updated` filters `\DosDevices\...` symbolic links, extracts their target device names, and calls `mountmgr_process_drive`.

`mountmgr_process_drive` scans known Btrfs child devices, compares their `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME` result to the mountmgr device name, removes the drive letter if the child belongs to this driver, and marks `had_drive_letter` so removal teardown can restore it later if needed.

## PnP Notification Wrappers

The file wraps notification callbacks with queued work items:

- `enqueue_pnp_callback` copies the symbolic link name and queues `do_pnp_callback`.
- `volume_notification` routes volume interface arrival/removal to `volume_arrival2` or `volume_removal`.
- `pnp_notification` routes disk interface arrival/removal to `disk_arrival` or `volume_removal`.

This avoids doing expensive probing while still in the notification callback.

## Integration Points

This file interacts with global driver state: `pdo_list`, `pdo_list_lock`, `registry_path`, `mountmgr_thread_event`, `mountmgr_thread_handle`, `shutting_down`, `busobj`, `boot_lock`, `drvobj`, and `master_devobj`. It depends on helper APIs such as `dev_ioctl`, `sync_read_phys`, `check_superblock_checksum`, `add_volume_device`, `pnp_surprise_removal`, `mountmgr_add_drive_letter`, and Windows storage/mountmgr IOCTLs.

## Risks And Notes

- `register_fve_callback` appears to leak the allocated `fve_data` if `IoRegisterPlugPlayNotification` fails, because it logs and returns without freeing `d`.
- `remove_volume_child` has non-obvious lock ownership: it releases `pdode->child_lock` internally. Callers must not release it again after this function succeeds through that path.
- PnP/mountmgr paths are race-prone by nature; this file uses locks and work items, but correctness depends on object references and list membership remaining valid across notification interleavings.

# File Research: sources/windows/winbtrfs/src/search.c

## Purpose

`search.c` implements WinBtrfs discovery and mount-manager integration for physical disks and volumes. It reacts to PnP interface notifications, probes candidate devices for Btrfs superblocks, creates or removes WinBtrfs volume children, handles BitLocker/FVE unlock notifications, and removes native drive letters from underlying child devices when WinBtrfs owns a multi-device filesystem.

## Global Integration

The file relies on driver globals including `pdo_list`, `pdo_list_lock`, `registry_path`, `mountmgr_thread_event`, `mountmgr_thread_handle`, `shutting_down`, `busobj`, `boot_lock`, `drvobj`, `master_devobj`, and optional `fIoUnregisterPlugPlayNotificationEx`. It maintains:

- `fve_data_list`, guarded by `fve_data_lock`, for locked BitLocker/FVE volumes that should be retried after an unlock event.
- A work-item based callback queue so PnP notification callbacks schedule discovery/removal work outside the notification path.

## Ignored Filesystems

- `fs_ignored()` formats the filesystem UUID as a registry subkey under `registry_path`, opens or creates that key, reads a DWORD value named `Ignore`, and returns whether the filesystem should be skipped. This lets configuration suppress automatic mounting for a specific Btrfs UUID.

## FVE/BitLocker Handling

- `test_vol()` treats `STATUS_FVE_LOCKED_VOLUME` specially. On initial discovery it registers a target-device change notification instead of mounting. On an FVE callback retry it returns `false` when the volume remains locked.
- `register_fve_callback()` stores the device path and registers `event_notification()` for `GUID_IO_VOLUME_FVE_STATUS_CHANGE`, avoiding duplicate registrations for the same device object.
- `event_notification()` filters target-device notifications to FVE status changes, finds the stored device path, allocates a work item, and queues `fve_callback()`.
- `fve_callback()` retries `volume_arrival()` with `fve_callback=true`; if the volume can now be mounted, it unregisters and frees the stored FVE notification record.

## Volume Probing

- `test_vol()` determines sector size from `DeviceObject->SectorSize` or `IOCTL_DISK_GET_DRIVE_GEOMETRY`, reads the primary Btrfs superblock, validates magic and checksum, then scans backup superblocks and keeps the newest valid generation. If the UUID is not ignored, it clears `DO_VERIFY_VOLUME` and calls `add_volume_device()` with disk number, partition number, path, and length.
- `disk_arrival()` handles whole-disk device arrivals. It ignores disks with partitions, reads length and storage device number, then calls `test_vol()` for partitionless whole-disk filesystems.
- `volume_arrival()` handles volume interface arrivals. It avoids devices created by this driver, tries `IOCTL_VOLUME_ONLINE`, reads length and storage device number, removes any already-mounted whole-disk child when a real partition appears for the same disk, then calls `test_vol()`.

## Removal and Child Device Handling

- `remove_volume_child()` removes a child device from a WinBtrfs PDO. It unregisters PnP notifications, surprise-removes the mounted filesystem unless degraded mounting allows the child to go missing, disables the device interface when appropriate, restores underlying drive letters previously removed from mountmgr, marks the corresponding Btrfs `device` as missing for degraded mounts, updates removable-media characteristics, dereferences and frees child resources, decrements `children_loaded`, and deletes the volume device when the last child is gone and no opens remain.
- `volume_removal()` normalizes `\\??\\`/`\??\` style prefixes, finds the matching child by PnP name, and removes it unless it is marked as the boot volume.

## PnP Callback Queue

- `pnp_callback` is a function pointer type for path-based PnP work.
- `pnp_callback_context` stores a copied `UNICODE_STRING`, callback function, and work item.
- `enqueue_pnp_callback()` copies the symbolic link name and queues `do_pnp_callback()` on `master_devobj`.
- `volume_notification()` queues `volume_arrival2()` on interface arrival and `volume_removal()` on removal.
- `pnp_notification()` queues `disk_arrival()` on disk interface arrival and `volume_removal()` on removal.

## Mount Manager Integration

- `remove_drive_letter()` builds a `MOUNTMGR_MOUNT_POINT` for a device name and calls `IOCTL_MOUNTMGR_DELETE_POINTS`, retrying with the reported output size when mountmgr returns `STATUS_BUFFER_OVERFLOW`.
- `mountmgr_process_drive()` walks WinBtrfs children, queries each child device name with `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`, compares it with the mountmgr device name, deletes the mount point if it matches, and marks `vc->had_drive_letter` so it can be restored on child removal.
- `mountmgr_updated()` scans all mount points and processes only `\DosDevices\...` symbolic links.
- `mountmgr_thread()` opens `MOUNTMGR_DEVICE_NAME`, waits for `IOCTL_MOUNTMGR_CHANGE_NOTIFY`, queries all mount points after each change, calls `mountmgr_updated()`, exits when `shutting_down` is set or an unrecoverable mountmgr error occurs, dereferences the mountmgr file object, clears `mountmgr_thread_handle`, and terminates the system thread.

## Locking and Lifetime

- `boot_lock` serializes discovery and arrival/removal operations around boot-time setup.
- `pdo_list_lock` protects the global PDO list; each PDO's `child_lock` protects child lists and removal state.
- FVE notification records are protected by a spin lock because they are touched from notification and worker contexts.
- File objects acquired by `IoGetDeviceObjectPointer()` are dereferenced on exit paths, and queued contexts own their copied paths.

## Notable Details

- The probing path validates superblock checksums and selects the highest-generation backup superblock, which avoids mounting from a stale primary when a newer valid backup exists.
- Whole-disk filesystem handling is conservative: once a partition for the same disk appears, an existing whole-disk child is removed.
- Degraded mounts are treated differently on child removal: the mounted filesystem can remain, and the missing device is marked by clearing the internal device object's `devobj`.
- Mount manager handling intentionally strips drive letters from underlying component volumes and restores them when the WinBtrfs child is removed.

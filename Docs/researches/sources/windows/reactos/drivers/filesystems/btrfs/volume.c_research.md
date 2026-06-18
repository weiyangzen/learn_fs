# File Research: sources/windows/reactos/drivers/filesystems/btrfs/volume.c

## Role

This file implements the WinBtrfs/ReactOS Btrfs volume-device layer: create/close dispatch for volume device objects, raw volume read/write forwarding, mountdev and volume IOCTL handling, mount manager drive-letter coordination, PnP removal notification, degraded-mount policy lookup, and discovery/registration of physical devices that belong to a Btrfs filesystem UUID.

It sits between Windows volume/mount-manager interfaces and the filesystem VCB/device model. It aggregates one or more `volume_child` devices under a `pdo_device_extension`, exposes a volume device extension to the rest of the driver, and forwards certain operations to child disk devices when safe.

## Major Responsibilities

- Maintain open/close lifetime for `volume_device_extension` objects.
- Tear down volume/PDO state in `free_vol()`, including children, PnP notifications, names, resources, detach/delete operations, and mounted-device back references.
- Forward raw volume reads and writes to the first child device, while rejecting raw writes when the Btrfs volume has more than one child device.
- Serve mountdev identifiers: device name, unique ID, stable GUID.
- Serve volume/disk/storage IOCTLs for dynamic volume status, writable checks, length, geometry, disk extents, GPT attributes, online notifications, media verification, and child passthrough.
- Ask mount manager to assign or remove drive letters.
- React to target-device query-remove notifications by asking the mounted filesystem device to query-remove.
- Check registry policy for degraded mounting, globally and per filesystem UUID.
- Add discovered physical devices to the global PDO list, create a PDO when first seeing a filesystem UUID, insert child devices in generation order, attach newly available child devices to an already mounted VCB, enable the volume interface when enough devices are present, and trigger bus relation updates or no-PnP attachment paths.

## Volume Lifetime

`vol_create()` rejects opens while `vde->removing` is set, otherwise reports `FILE_OPENED` and increments `open_count`.

`vol_close()` decrements `open_count` under `pdo_list_lock` and the PDO child lock. If the last handle closes after removal was requested, it calls `free_vol()`. It also guards against `vde->dead` before and after acquiring the global lock.

`free_vol()` marks the volume dead, disconnects `Vcb->vde` from any mounted device, frees the symbolic name buffer, deletes `pdode->child_lock`, detaches from an attached device if present, unregisters every child PnP notification, frees child PnP names and child records, frees a manually allocated PDO extension in `no_pnp` mode, deletes the volume FDO, and deletes the PDO when normal PnP is in use.

## Raw Read And Write Forwarding

`vol_read()` and `vol_write()` allocate a new IRP targeted at a child device because the target device is not in this driver's stack. Both hold `pdode->child_lock` while choosing the child and waiting for completion.

Read forwarding:

- Requires at least one child.
- Uses the first child.
- Builds an IRP with `IRP_MJ_READ` and the child file object.
- Handles buffered I/O by allocating a system buffer and setting `IRP_BUFFERED_IO | IRP_DEALLOCATE_BUFFER | IRP_INPUT_OPERATION`; direct I/O reuses the caller MDL; neither-buffered/direct maps the caller MDL to a system address.
- Copies read length and byte offset, waits for completion, copies `Information` back, completes the original IRP.

Write forwarding:

- Requires at least one child.
- Rejects writes when more than one child is present, returning `STATUS_ACCESS_DENIED`.
- Builds an `IRP_MJ_WRITE` similarly to read forwarding.
- For buffered I/O it points the child IRP system buffer and user buffer at the mapped caller buffer, without allocating a new copy.
- Waits synchronously, propagates status and byte count, completes the original IRP.

## IOCTL Handling

`vol_device_control()` dispatches known control codes directly and otherwise tries `vol_ioctl_passthrough()` when the volume has exactly one child.

Direct handlers include:

- `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`: returns `vde->name` as `MOUNTDEV_NAME`.
- `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`: returns the filesystem UUID from `pdode->uuid`.
- `IOCTL_STORAGE_GET_DEVICE_NUMBER`: returns the child disk and partition number only for a single child with a valid disk number.
- `IOCTL_MOUNTDEV_QUERY_STABLE_GUID`: returns the filesystem UUID as the stable GUID.
- `IOCTL_VOLUME_GET_GPT_ATTRIBUTES`: returns zero GPT attributes.
- `IOCTL_VOLUME_IS_DYNAMIC`: writes one byte set to `1`.
- `IOCTL_VOLUME_ONLINE` and `IOCTL_VOLUME_POST_ONLINE`: no-op success.
- `IOCTL_DISK_GET_DRIVE_GEOMETRY`: synthesizes CHS geometry from total child size and device sector size.
- `IOCTL_DISK_IS_WRITABLE`: probes children with `IOCTL_DISK_IS_WRITABLE`.
- `IOCTL_DISK_GET_LENGTH_INFO`: sums child `vc->size`.
- `IOCTL_STORAGE_CHECK_VERIFY` and `IOCTL_DISK_CHECK_VERIFY`: checks every child with `IOCTL_STORAGE_CHECK_VERIFY`.
- `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`: aggregates disk extents from every child.

`vol_ioctl_passthrough()` rejects zero-child and multi-child volumes, allocates a child IRP, copies major/minor function, IOCTL parameters, buffers, MDL, user buffer, and flags, waits for completion, copies status and information back, then frees the IRP.

## Disk Extents, Length, Geometry, Writability

`vol_get_disk_extents()` first counts the extents returned by every child, tracks the largest child response needed, then either reports `STATUS_BUFFER_OVERFLOW` with the required count or re-queries each child and concatenates all `DISK_EXTENT` entries into the caller buffer.

`vol_get_length()` sums `volume_child.size` across all children.

`vol_get_drive_geometry()` sums child sizes and reports a synthetic geometry with sector size from `DeviceObject->SectorSize` or 512 bytes, 63 sectors per track, 255 tracks per cylinder, and removable/fixed media based on device characteristics.

`vol_is_writable()` checks whether any child accepts `IOCTL_DISK_IS_WRITABLE` and tracks `STATUS_MEDIA_WRITE_PROTECTED` versus other errors. The function computes a `Status`, but currently returns `STATUS_SUCCESS` unconditionally after releasing the child lock, which weakens write-protection reporting.

## Mount Manager And Drive Letters

`mountmgr_add_drive_letter()` sends `IOCTL_MOUNTMGR_NEXT_DRIVE_LETTER` for a device path and logs whether a drive letter was assigned.

`drive_letter_callback2()` snapshots child PnP names into a temporary list, removes existing drive-letter links through mount manager, records whether each child previously had a letter in `vc->had_drive_letter`, and frees temporary records. It deliberately drops `child_lock` while calling mount manager, then reacquires it to update matching children by device UUID.

`drive_letter_callback()` obtains the mount manager device object and invokes `drive_letter_callback2()`.

## PnP And Degraded Mounts

`pnp_removal()` handles `GUID_TARGET_DEVICE_QUERY_REMOVE` by delegating query-remove to the mounted filesystem device when present.

`allow_degraded_mount()` builds a registry subkey path under the driver registry path using the filesystem UUID string. It defaults to global `mount_allow_degraded`, opens the per-UUID key if present, reads a `REG_DWORD` value named `AllowDegraded`, and returns the resulting boolean value.

## Device Discovery And PDO Aggregation

`add_volume_device()` is the core discovery path for a device containing a Btrfs superblock:

- Ignores empty device paths.
- Acquires the global `pdo_list_lock` and searches for an existing `pdo_device_extension` by filesystem UUID.
- Opens the target device with `IoGetDeviceObjectPointer`.
- If this is the first device for the filesystem UUID, creates a PDO using either `IoReportDetectedDevice` plus manual extension allocation in `no_pnp` mode or `IoCreateDevice` with `FILE_AUTOGENERATED_DEVICE_NAME | FILE_DEVICE_SECURE_OPEN` in normal PnP mode.
- Initializes the PDO extension, child list, child count, sector size, and resources.
- For existing PDOs, rejects duplicate child device UUIDs.
- Allocates and populates a `volume_child` with device UUID, devid, generation, PnP notification handle, device/file objects, normalized PnP name, size, seeding flag, disk/partition numbers, and drive-letter state.
- Inserts the child ordered by generation, updating `pdode->num_children` from the newest superblock when appropriate.
- If the filesystem is already mounted, finds a matching missing `device` entry in the VCB and initializes it.
- Propagates removable-media characteristics.
- Enables the volume interface and processes drive letters when all expected children are loaded or one child is loaded and degraded mounting is allowed.
- Inserts new PDOs into the global list after child setup, then notifies boot/no-PnP/bus paths.

The `fail:` path dereferences the opened `FileObject`. Several earlier failure branches return without reaching `fail`, so this function relies on the exact branch structure for object lifetime.

## Dependencies And Integration Points

This file depends on driver globals (`drvobj`, `master_devobj`, `busobj`, `pdo_list_lock`, `pdo_list`, `registry_path`), volume/PDO structures from `btrfs_drv.h`, mount manager APIs, raw child-device `dev_ioctl()`, filesystem removal logic (`pnp_query_remove_device()`), device initialization (`init_device()`), boot attach (`boot_add_device()`), `AddDevice()`, drive-letter removal helpers, and global options such as `no_pnp`, `mount_allow_degraded`, and `boot_uuid`.

## Risk Notes

- `vol_is_writable()` ignores its computed failure status and always returns success.
- `vol_read()` allocates a child IRP and may allocate a buffered I/O system buffer, but the visible code does not free `Irp2` on all completion paths; correctness depends on IRP flags/completion behavior outside this file.
- Raw writes are intentionally limited to single-child volumes; multi-device Btrfs raw volume writes are denied.
- `vol_ioctl_passthrough()` copies the original IRP flags and buffer pointers to a separate IRP, so passthrough correctness depends on the target driver's interpretation of borrowed buffers and the synchronous wait.
- `add_volume_device()` mixes global PDO locking, child locking, device-object references, and no-PnP special handling; error-path lifetime is subtle.

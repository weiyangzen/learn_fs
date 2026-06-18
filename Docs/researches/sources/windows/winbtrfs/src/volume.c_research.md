# File Research: sources/windows/winbtrfs/src/volume.c

## Purpose

`volume.c` implements WinBtrfs' volume device wrapper and physical-device aggregation for Btrfs filesystems. It creates logical volume devices over one or more child block devices, forwards raw reads and selected writes, answers mount manager/storage IOCTLs, registers PnP removal notifications, handles drive-letter cleanup, and adds discovered Btrfs devices to the driver's PDO list.

The code bridges Windows volume/mount-manager expectations with Btrfs' multi-device model.

## Volume Lifetime

`vol_create` rejects opens during removal, increments `open_count`, and reports `FILE_OPENED`. `vol_close` decrements `open_count` under `pdo_list_lock` and the PDO child lock; if the volume is marked removing and the last handle closes, it calls `free_vol`.

`free_vol` marks the volume dead, detaches it from any mounted VCB, frees its name, deletes child locks, detaches/deletes device objects, unregisters child PnP notifications, frees child PnP names, and handles the `no_pnp` PDO allocation mode.

## Raw Read/Write Forwarding

`vol_read` forwards an IRP read to the first child device. It allocates a new lower IRP because the child is not in the same device stack, maps buffered/direct/neither I/O according to the child device flags, installs `vol_read_completion`, waits synchronously if pending, copies completion information back to the original IRP, and completes the original request.

`vol_write` mirrors this flow for writes but only permits writes when there is exactly one child device. Multi-device raw volume writes return `STATUS_ACCESS_DENIED`, preventing a caller from writing arbitrary bytes to just the first member of a Btrfs multi-device filesystem.

The shared completion context stores an `IO_STATUS_BLOCK` and event.

## IOCTL Handling

`vol_device_control` handles mountdev, disk, storage, and volume IOCTLs:

- `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`: returns the logical volume name.
- `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`: returns the filesystem UUID from the PDO extension.
- `IOCTL_STORAGE_GET_DEVICE_NUMBER`: returns the child disk/partition number for single-device volumes.
- `IOCTL_MOUNTDEV_QUERY_STABLE_GUID`: returns the filesystem UUID as a stable GUID.
- `IOCTL_VOLUME_GET_GPT_ATTRIBUTES`: returns zero attributes.
- `IOCTL_VOLUME_IS_DYNAMIC`: returns a one-byte true value.
- `IOCTL_VOLUME_ONLINE` and `IOCTL_VOLUME_POST_ONLINE`: succeed without work.
- `IOCTL_DISK_GET_DRIVE_GEOMETRY`: synthesizes geometry from aggregate child size and sector size.
- `IOCTL_DISK_IS_WRITABLE`: checks whether any child accepts `IOCTL_DISK_IS_WRITABLE`.
- `IOCTL_DISK_GET_LENGTH_INFO`: returns aggregate child size.
- `IOCTL_STORAGE_CHECK_VERIFY` and `IOCTL_DISK_CHECK_VERIFY`: checks all children.
- `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`: aggregates disk extents from all children.

Unknown IOCTLs are passed through only when the logical volume has one child (`vol_ioctl_passthrough`). The passthrough routine creates a lower IRP, mirrors the caller's IOCTL parameters and buffers, waits for completion, copies the lower status/information, and frees the lower IRP.

Note: `vol_is_writable` computes `STATUS_MEDIA_WRITE_PROTECTED` when no child is writable but returns `STATUS_SUCCESS` unconditionally at the end. That may be intentional compatibility behavior or a latent bug; the local `Status` value is otherwise unused on return.

## Mount Manager and Drive Letters

`mountmgr_add_drive_letter` asks MountMgr for the next drive letter for a given device path with `IOCTL_MOUNTMGR_NEXT_DRIVE_LETTER`.

`drive_letter_callback` opens `MOUNTMGR_DEVICE_NAME` and calls `drive_letter_callback2`. The latter builds `\\??`-prefixed names for all child PnP paths, removes their existing drive letters, then reacquires the child lock and records whether each child previously had a drive letter. This supports replacing per-device letters with the logical Btrfs volume letter.

## PnP Removal and Degraded Mount Policy

`pnp_removal` listens for `GUID_TARGET_DEVICE_QUERY_REMOVE` and forwards query-remove handling to the mounted filesystem device when present.

`allow_degraded_mount` reads the global `mount_allow_degraded` default and then checks the per-volume registry key `<registry_path>\<filesystem-uuid>` for a DWORD `AllowDegraded` override. `add_volume_device` uses this to decide whether a partially discovered filesystem may be surfaced.

## Adding Discovered Devices

`add_volume_device` is called when a Btrfs superblock/device is discovered. It:

- Finds or creates a PDO extension keyed by filesystem UUID.
- Opens the physical device path and stores the file/device object.
- Initializes child list state and sector size for new PDOs.
- Rejects duplicate device UUIDs.
- Allocates a `volume_child` with device UUID, device id, generation, size, disk/partition numbers, seeding flag, and normalized PnP path.
- Registers target-device-change notifications.
- Inserts the child ordered by generation, updating expected child count when newer metadata appears.
- If the filesystem is already mounted, attaches the physical device to the matching missing Btrfs `device` record and calls `init_device`.
- Propagates removable-media characteristics.
- Enables the device interface once all children are loaded, or once one child is loaded and degraded mount is allowed.
- Processes drive-letter cleanup, inserts new PDOs into `pdo_list`, and triggers boot/no-PnP/bus relation handling as appropriate.

Failure paths dereference the opened file object. Some new-PDO failure branches return after allocation/open failures without central cleanup, so ownership must be read carefully when modifying this function.

## Dependencies and Cross-File Interactions

This file depends on driver globals (`drvobj`, `master_devobj`, `busobj`, `pdo_list_lock`, `pdo_list`, `registry_path`), PnP helpers (`pnp_query_remove_device`, `boot_add_device`, `AddDevice`), IOCTL helper `dev_ioctl`, drive-letter helper `remove_drive_letter`, Btrfs device initialization `init_device`, and registry option state (`mount_allow_degraded`).

It shares major data structures with the rest of the driver: `volume_device_extension`, `pdo_device_extension`, `volume_child`, `device_extension`, `device`, `superblock`, and Btrfs UUID/device item fields.

## Error Handling and Safety Notes

The file uses ERESOURCE locking around global PDO and per-PDO child state. Raw lower IRP forwarding is synchronous and carefully separates the logical volume stack from child device stacks.

The most important behavioral safety boundaries are multi-device write denial, single-child IOCTL passthrough only, duplicate child UUID rejection, and query-remove propagation to mounted filesystems.

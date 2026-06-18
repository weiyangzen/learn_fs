# File Research: sources/windows/reactos/drivers/filesystems/btrfs/devctrl.c

Implements device-control dispatch for the Btrfs driver’s control, filesystem, and volume device objects. It handles a small set of driver/private IOCTLs directly, answers mount-manager/disk writability queries for filesystem devices, delegates volume-device controls, and forwards unknown filesystem-device controls to the underlying real disk device.

Key entry points:
- `drv_device_control()` is the `IRP_MJ_DEVICE_CONTROL` dispatcher. It enters filesystem context, detects top-level IRPs, routes control devices to `control_ioctl()`, volume devices to `vol_device_control()`, filesystem devices to local mount/disk handlers, and forwards unhandled control codes to `Vpb->RealDevice`.
- `control_ioctl()` handles driver control-device IOCTLs: `IOCTL_BTRFS_QUERY_FILESYSTEMS`, `IOCTL_BTRFS_PROBE_VOLUME`, and `IOCTL_BTRFS_UNLOAD`.
- `mountdev_query_stable_guid()` returns the mounted filesystem UUID as the mount manager stable GUID.
- `is_writable()` implements `IOCTL_DISK_IS_WRITABLE` by returning `STATUS_MEDIA_WRITE_PROTECTED` when the VCB is readonly.
- `query_filesystems()` serializes the currently loaded Btrfs filesystems from global `VcbList`, including filesystem UUIDs, device UUIDs, missing-device markers, and mountdev device names.
- `probe_volume()` validates a supplied mountdev name, requires `SE_MANAGE_VOLUME_PRIVILEGE`, opens the target device, refreshes disk properties when applicable, gets the PnP name/interface GUID, runs removal notification, then reannounces the disk or volume.
- `ioctl_unload()` requires `SE_LOAD_DRIVER_PRIVILEGE` and invokes `do_shutdown()`.

Important behavior:
- `query_filesystems()` holds `global_loading_lock` while walking `VcbList`, and each VCB’s `tree_lock` while reading device lists and superblock device counts.
- Variable-length filesystem/device output uses `next_entry` offsets for filesystem records and embeds variable-length device names after each `btrfs_filesystem_device`.
- Missing devices are reported without a mountdev name; present devices are queried through `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`.
- `probe_volume()` accepts a `MOUNTDEV_NAME` input buffer from the caller, converts it to a `UNICODE_STRING`, opens the named device with `IoGetDeviceObjectPointer()`, and triggers arrival/removal paths to refresh driver discovery.
- `drv_device_control()` completes handled IRPs itself, but skips/completes through the lower driver for forwarded IOCTLs.

Filesystem relevance:
- This file is the administrative/control surface for enumerating loaded Btrfs volumes, rescanning/probing devices, unloading the driver, exposing a stable mount GUID, and preserving Windows disk IOCTL behavior.

Notable risks:
- `query_filesystems()` has complex variable-length packing; callers depend on accurate `itemsize`, `next_entry`, and remaining-length accounting.
- The present-device branch fills name data but does not visibly initialize every per-device output field, so structure layout and caller zeroing expectations are important.
- `control_ioctl()` returns data for `IOCTL_BTRFS_QUERY_FILESYSTEMS` but does not set `Irp->IoStatus.Information` itself; if the API expects bytes-returned semantics, that should be checked against callers.
- `probe_volume()` privilege-gates rescans correctly, but its lifetime/ownership contract for the PnP name returned by `get_device_pnp_name()` should be confirmed with that helper.

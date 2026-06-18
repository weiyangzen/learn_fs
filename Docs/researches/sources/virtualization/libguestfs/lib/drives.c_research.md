# File Research: sources/virtualization/libguestfs/lib/drives.c

## Role
Manages the `guestfs_h` drive array and all metadata needed to add file, network, remote, scratch, read-only, and special drives before appliance launch.

## Drive Creation
- File drives store path, format, name, disk label, cache mode, readonly flag, discard mode, copy-on-read flag, and block size.
- Non-file drives store protocol, servers, export name, username, secret, and format.
- Read-only drives create backend-specific COW overlays so original storage is protected.
- `/dev/null` drives are replaced with a temporary 4 KiB raw file.
- A dummy drive slot is used internally for the appliance.

## Protocol Validation
Supports file, ftp, ftps, http, https, iscsi, nbd, rbd, and ssh. Protocol-specific validation covers server count, transport type, path/export syntax, username/secret support, and default NBD port.

## Option Validation
- Format must be alphanumeric plus `-_`.
- Disk label must be alphabetic and at most 20 characters.
- Cache mode is limited to `writeback` or `unsafe`.
- Discard is `disable`, `enable`, or `besteffort`.
- Block size must be 512 or 4096.
- Read-only drives cannot enable discard.

## Public APIs
- `guestfs_impl_add_drive_opts()` is the main add path and only works in `CONFIG` state; hotplugging returns an error.
- `guestfs_impl_add_drive_ro()`, `add_drive_with_if()`, `add_drive_ro_with_if()`, and `add_cdrom()` are compatibility wrappers.
- `guestfs_impl_add_drive_scratch()` creates a temporary raw disk and adds it with unsafe cache mode.
- `guestfs_impl_remove_drive()` reports removed hotplug support.
- Checkpoint/rollback helpers support atomic drive additions.
- `guestfs_impl_debug_drives()` returns textual drive descriptions.
- `guestfs_impl_device_index()` and `guestfs_impl_device_name()` convert between `/dev/sd*` names and drive indexes.

## Filesystem/Storage Relevance
This file is the main host-side model for storage sources presented to the appliance, including protection overlays, remote block protocols, scratch disks, labels, discard behavior, and block size selection.

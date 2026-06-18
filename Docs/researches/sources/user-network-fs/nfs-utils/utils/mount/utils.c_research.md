<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.c -->
# sources/user-network-fs/nfs-utils/utils/mount/utils.c

## Purpose

`utils.c` contains miscellaneous shared helpers for `mount.nfs` and `umount.nfs`: kernel mount-data version selection, verbose mount printing, usage text, mountpoint validation, and NFSv2/v3 unmount setup.

## Important APIs, types, and functions

`discover_nfs_mount_data_version` maps the running kernel release to legacy binary `nfs_mount_data` versions and indicates when string options are supported. `print_one`, `mount_usage`, and `umount_usage` handle user output. `chk_mountpoint` validates the local target. `nfs_umount23` parses the device name and option string, then invokes `nfs_umount_do_umnt`.

## Control flow

Version discovery reads `linux_version_code` and applies historical kernel thresholds. `chk_mountpoint` stats the mountpoint, requires a directory, and for non-root users checks execute permission. `nfs_umount23` parses `hostname:path`, splits mtab options with `po_split`, calls the network unmount helper, and frees all temporary allocations.

## State and persistence behavior

The file has no durable state. It reads kernel version and filesystem metadata, emits messages, and passes parsed options to the unmount RPC path. It relies on globals `verbose` and `progname` for output behavior.

## Dependencies and integration points

It depends on `version.h`, `parse_opt`, `parse_dev`, mount error reporting, network unmount helpers, NLS, and support headers for NFS mount constants. It is linked into the mount/umount utilities.

## Risks and edge cases

Kernel-version parsing failures return `UINT_MAX`, which suppresses old compatibility paths and treats the kernel as future/new. `nfs_umount23` tolerates option parse failure only by returning an error before RPC unmount. Access checks differ for real/effective root.

## Test signals

Tests should cover kernel threshold mappings, malformed kernel releases, non-directory mountpoints, permission failures for non-root users, malformed NFS device names, empty option strings, and option parsing failures on quoted strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mount/utils.c -->

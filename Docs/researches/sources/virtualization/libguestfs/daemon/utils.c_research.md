# File Research: sources/virtualization/libguestfs/daemon/utils.c

## Role
Provides shared daemon utility state and helpers for device classification, sysroot path construction, robust I/O, string-list management, mountable parsing, udev settling, UUID generation, and temporary exclude files.

## Global State
- Tracks `root_device`, `verbose`, `enable_network`, `sysroot`, `sysroot_len`, `autosync_umount`, and `test_mode`.
- `sysroot` defaults to `/sysroot`.

## Device and Path Helpers
- `is_root_device()` compares device `st_rdev` against the appliance root device.
- `is_device_parameter()` accepts `/dev/...` disk-like block devices, rejects the appliance root device, handles `/dev/sd*` translation compatibility, and verifies `BLKGETSIZE64`.
- `sysroot_path()` prepends `/sysroot`.
- `sysroot_realpath()` resolves a path inside chroot and maps it back to sysroot.

## Utility Infrastructure
- `xwrite()` and `xread()` perform complete writes/reads.
- `stringsbuf` helpers build NULL-terminated string vectors.
- `split_lines()` implements command-output line splitting with documented corner-case behavior.
- `filter_list()`, `trim()`, `sort_strings()`, and `empty_list()` provide common list/string operations.

## Mountable and External State
- `parse_btrfsvol()` parses `btrfsvol:/dev/.../subvol` descriptors and resolves the backing device.
- `mountable_to_string()` converts mountable structs back to text.
- `prog_exists()` searches `$PATH`.
- `random_name()` substitutes random base36 characters into path templates.
- `udev_settle_file()` wraps `udevadm settle`.
- `get_random_uuid()` wraps `uuidgen`.
- `make_exclude_from_file()` writes tar/rsync-style exclude patterns to a temp file.

## Filesystem/Storage Relevance
This file is central daemon plumbing for safe guest path handling, block-device recognition, btrfs subvolume mountables, udev consistency after device changes, and file-list construction.

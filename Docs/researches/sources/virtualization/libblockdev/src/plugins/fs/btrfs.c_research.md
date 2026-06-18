# File Research: sources/virtualization/libblockdev/src/plugins/fs/btrfs.c

## Role

`btrfs.c` implements filesystem-plugin operations for single-device Btrfs filesystems. It deliberately directs more complicated multi-device setups to the separate Btrfs plugin.

## Dependency Model

The module caches runtime dependency checks for:

- `mkfs.btrfs`
- `btrfsck`
- `btrfs`
- `btrfstune`

`bd_fs_btrfs_is_tech_avail()` maps filesystem modes to required utilities:

- mkfs: `mkfs.btrfs`
- check/repair: `btrfsck`
- set-label/query/resize: `btrfs`
- set-uuid: `btrfstune`
- wipe: no extra dependency here

`_fs_btrfs_reset_avail_deps()` resets the cache.

## Info Object

`BDFSBtrfsInfo` contains label, UUID, total size, and computed free space.

`bd_fs_btrfs_info_copy()` and `bd_fs_btrfs_info_free()` handle heap ownership.

## mkfs Options and Creation

`bd_fs_btrfs_mkfs_options()` converts generic mkfs options into Btrfs command arguments:

- label -> `-L`
- UUID -> `-U`
- no discard -> `-K`
- force -> `-f`
- caller extra args appended after generated args

`bd_fs_btrfs_mkfs()` runs `mkfs.btrfs <device>` with any extra arguments.

## Check and Repair

`bd_fs_btrfs_check()` runs `btrfsck <device>`.

`bd_fs_btrfs_repair()` runs `btrfsck --repair <device>`.

Both delegate command execution and error reporting to libblockdev utilities.

## Label and UUID

`bd_fs_btrfs_set_label()` runs `btrfs filesystem label <mpoint> <label>`.

`bd_fs_btrfs_check_label()` enforces maximum length 256 and rejects newlines.

`bd_fs_btrfs_set_uuid()` runs `btrfstune -u <device>` to generate a UUID or `btrfstune -U <uuid> <device>` for a supplied UUID. It writes `"y\n"` to acknowledge btrfstune confirmation.

`bd_fs_btrfs_check_uuid()` delegates to the common RFC-4122 UUID validator.

## Query and Resize

`bd_fs_btrfs_get_info()` runs `btrfs filesystem show --raw <mpoint>` and parses label, UUID, device count, and device size with a GLib regex. It rejects multi-device filesystems. It then runs `btrfs inspect-internal min-dev-size <mpoint>`, parses the minimum size, and reports `free_space = size - min_size`.

`bd_fs_btrfs_resize()` first calls `bd_fs_btrfs_get_info()` to reject multi-device volumes, then runs `btrfs filesystem resize <size-or-max> <mpoint>`.

## Notable Risks

- Output parsing depends on `btrfs` CLI text formats.
- Multi-device Btrfs is intentionally unsupported here.
- `free_space` is derived from current size minus minimum device size, not general filesystem free space.
- UUID setting programmatically confirms btrfstune's prompt.

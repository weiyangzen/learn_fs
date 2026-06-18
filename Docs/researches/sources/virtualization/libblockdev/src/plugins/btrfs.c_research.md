# File Research: sources/virtualization/libblockdev/src/plugins/btrfs.c

## Role
Implementation of the libblockdev Btrfs plugin. It provides Btrfs volume, device, subvolume, snapshot, filesystem, label, check/repair, resize, and device-stat APIs.

## Dependencies
- Requires the `btrfs` userspace utility at minimum version `3.18.2`.
- Recursive subvolume deletion requires `btrfs` version `6.12`.
- Requires the kernel `btrfs` module for plugin availability checks.
- Uses libbytesize to parse human-readable size strings from `btrfs filesystem show`.
- Uses Linux Btrfs ioctls for device statistics.

## Data Types and Memory Helpers
- Implements copy/free helpers for:
  - `BDBtrfsDeviceInfo`;
  - `BDBtrfsSubvolumeInfo`;
  - `BDBtrfsFilesystemInfo`;
  - `BDBtrfsDeviceStats`.
- Each copy helper deep-copies owned strings; each free helper releases strings and the struct.
- `bd_btrfs_error_quark()` defines the plugin error domain.

## Dependency Checking
- Static atomic bitmasks cache discovered utility/module availability.
- `bd_btrfs_init()` is a no-op returning TRUE.
- `bd_btrfs_close()` clears cached dependency state.
- `bd_btrfs_is_tech_avail()` checks base Btrfs utility and kernel module dependencies for all technologies, plus the `6.12` dependency for recursive subvolume deletion.

## Command-Based Operations
- `bd_btrfs_create_volume()` validates a non-empty device list, verifies each path exists, builds `mkfs.btrfs` arguments, and supports optional label, data RAID level, metadata RAID level, and extra arguments.
- `bd_btrfs_mkfs()` is an alias around `bd_btrfs_create_volume()`.
- `bd_btrfs_add_device()` runs `btrfs device add`.
- `bd_btrfs_remove_device()` runs `btrfs device delete`.
- `bd_btrfs_create_subvolume()` builds `mountpoint/name` and runs `btrfs subvol create`.
- `bd_btrfs_delete_subvolume()` delegates to `bd_btrfs_delete_subvolume_recursive()` with `recursive=FALSE`.
- `bd_btrfs_delete_subvolume_recursive()` optionally adds `--recursive`, requiring btrfs-progs 6.12 when recursive.
- `bd_btrfs_set_default_subvolume()` runs `btrfs subvol set-default <id> <mountpoint>`.
- `bd_btrfs_create_snapshot()` runs `btrfs subvol snapshot`, with `-r` for read-only snapshots.
- `bd_btrfs_resize()` runs `btrfs filesystem resize <size> <mountpoint>`.
- `bd_btrfs_check()` runs `btrfs check`.
- `bd_btrfs_repair()` runs `btrfs check --repair`.
- `bd_btrfs_change_label()` runs `btrfs filesystem label`.

## Query and Parsing Operations
- `bd_btrfs_get_default_subvolume_id()` runs `btrfs subvol get-default` and parses `ID <number>`.
- `bd_btrfs_list_devices()` runs `btrfs filesystem show`, scans lines with a regex for device id, size, used bytes, and path, and returns a NULL-terminated array.
- `bd_btrfs_list_subvolumes()` runs `btrfs subvol list -a -p`, optionally with `-s`, parses ID/parent/path output, and sorts returned subvolumes so parents/siblings precede children where possible.
- `bd_btrfs_filesystem_info()` runs `btrfs filesystem show` and parses label, UUID, number of devices, and used bytes.
- Empty output from subvolume listing is treated as a valid empty subvolume array when the utility reports no stdout.

## Ioctl-Based Device Stats
- `bd_btrfs_device_stats()` only checks the kernel module dependency, then opens the mountpoint read-only.
- Uses `BTRFS_IOC_FS_INFO` to learn device count and max id.
- Iterates device IDs, ignoring `ENODEV`, then uses `BTRFS_IOC_DEV_INFO` and `BTRFS_IOC_GET_DEV_STATS`.
- Returns per-device path and write/read/flush/corruption/generation error counters.
- Fails if no devices are found.

## Error Behavior
- Missing devices for volume creation produce `BD_BTRFS_ERROR_DEVICE`.
- Parse failures for queried command output produce `BD_BTRFS_ERROR_PARSE`.
- Utility execution errors are propagated through libblockdev utility helpers.
- Size parsing warnings are logged but do not necessarily fail the whole parsed record.

## Filesystem/Storage Relevance
This is the group’s main filesystem implementation file. It is not an in-kernel Btrfs implementation; it is a privileged userspace wrapper around btrfs-progs plus a small ioctl path for stats, exposing Btrfs administration through libblockdev's plugin API.

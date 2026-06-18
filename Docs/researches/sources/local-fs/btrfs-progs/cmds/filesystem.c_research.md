# File Research: sources/local-fs/btrfs-progs/cmds/filesystem.c

## Purpose
Implements the `btrfs filesystem` command group: `df`, `show`, `sync`, `defragment`, legacy `balance` alias, `resize`, `label`, `mkswapfile`, `commit-stats`, plus group registration for `du` and `usage`.

## Filesystem Space Display
- `cmd_filesystem_df()` opens a mount, calls `get_df()`, and prints text or JSON. Text mode also reads sysfs allocation files per block-group type.
- `print_df_text()` and `print_df_json()` include zone-unusable data when available.

## Filesystem Discovery
- `cmd_filesystem_show()` searches mounted filesystems, blkid-scanned devices, direct regular-file images, UUIDs, labels, devices, or mountpoints.
- Mounted scan uses `/proc/self/mounts`, `get_fs_info()`, `get_label_*()`, and `get_df()`.
- Unmounted scan copies the global scanned fs-device list, builds seed/sprout mappings by opening ctrees partially, and prints deduplicated fsids.
- `seen_fsid_hash` prevents duplicate output for filesystems mounted multiple times.

## Sync and Label
- `cmd_filesystem_sync()` delegates to `btrfs_util_fs_sync()`.
- `cmd_filesystem_label()` gets or sets labels through common label helpers.

## Defragment
- `cmd_filesystem_defrag()` parses recursive mode, compression type/level, no-compress, flush, byte range, target extent size, and step size.
- Defrag uses `BTRFS_IOC_DEFRAG_RANGE`; optional step mode repeatedly submits smaller ranges and starts IO after each step.
- Recursive directory defrag uses `nftw()` and skips crossing mounts/physical symlinks.
- The code warns when directories are passed without recursive mode because kernel directory defrag does not walk files.

## Resize
- `parse_resize_args()` handles `cancel`, optional `devid:`, `max`, absolute sizes, and +/- size deltas.
- Mounted resize validates device ids and new size, checks exclusive-operation state unless canceling, then calls `BTRFS_IOC_RESIZE`.
- `offline_resize()` supports unmounted single-device growth/max resize through direct ctree write, device item update, super total update, and regular-file truncation when applicable. Offline shrinking and multi-device filesystems are rejected.

## Swapfile and Commit Stats
- `cmd_filesystem_mkswapfile()` creates a new 0600 file, sets NOCOW, fallocates aligned size, and writes a v2 swap signature with UUID.
- `cmd_filesystem_commit_stats()` reads `commit_stats` from sysfs, maps known keys to user-facing labels, prints UUID when available, and can reset max commit duration with `-z/--reset`.

## Registration
The command group includes `df`, `du`, `show`, `commit-stats`, `sync`, `defragment`, hidden `balance` alias, `resize`, `label`, `usage`, and `mkswapfile`.

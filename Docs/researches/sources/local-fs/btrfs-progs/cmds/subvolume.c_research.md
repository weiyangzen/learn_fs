# File Research: sources/local-fs/btrfs-progs/cmds/subvolume.c

## Purpose
Implements the `btrfs subvolume` command group for btrfs-progs: create, delete, list integration, snapshot, get/set-default, find-new, show, and sync. It is CLI glue around `libbtrfsutil`, btrfs ioctls, qgroup helpers, formatting helpers, and common path/open/device utilities.

## Key Interfaces And Flow
- Defines `btrfs_subvolume_rowspec[]`, shared JSON/text output schema for subvolume fields, UUIDs, times, qgroup stats, and snapshot lists.
- `cmd_subvolume_create()` parses `-i` qgroup inheritance and `-p/--parents`, then calls `create_one_subvolume()` for each destination.
- `cmd_subvolume_delete()` supports path deletion, `--subvolid`, commit modes, recursive deletion printing, dry-run, default-subvolume protection, and final per-filesystem sync for `--commit-after`.
- `cmd_subvolume_snapshot()` validates source/destination, derives destination name when a directory is given, and creates read-write or read-only snapshots with optional qgroup inheritance.
- `cmd_subvolume_get_default()` and `cmd_subvolume_set_default()` query or set the default root by path or explicit root id.
- `cmd_subvolume_find_new()` uses tree-search ioctls to print file extents changed since a generation marker.
- `cmd_subvolume_show()` resolves a subvolume by path, root id, or UUID, prints metadata, child snapshots, and qgroup usage.
- `cmd_subvolume_sync()` waits for deleted subvolume ids to disappear, either explicitly supplied or discovered via `btrfs_util_subvolume_list_deleted_fd()`.
- Registers the command group through `subvolume_cmd_group` and `DEFINE_GROUP_COMMAND_TOKEN(subvolume)`.

## Dependencies
Uses `libbtrfsutil` for high-level subvolume operations, `BTRFS_IOC_INO_LOOKUP` and tree-search ioctls for low-level generation/path discovery, qgroup code from `cmds/qgroup.h`, formatter rowspecs from `common/format-output.h`, and many common path/open/message helpers.

## Notable Behaviors
- Delete protects the current default subvolume by comparing target id to `btrfs_util_subvolume_get_default_fd()`.
- Recursive delete is delegated to `BTRFS_UTIL_DELETE_SUBVOLUME_RECURSIVE`, but it first attempts a post-order iterator pass to print nested subvolumes.
- `--commit-after` keeps one fd per seen fsid so a final sync is issued once per filesystem.
- `find-new` syncs the filesystem before searching, then uses cached inode/path resolution to reduce repeated tree lookups.
- JSON output is conditionally enabled for some commands under `EXPERIMENTAL`.

## Risks And Review Notes
- `qgroup_inherit_add_group(struct ..., const char *arg)` ignores `arg` and reads global `optarg`; current callers pass `optarg`, but the function signature is misleading and fragile.
- `print_subvolume_show_text()` prints `Send time` before formatting `subvol->stime`, so send time appears to reuse the previous creation-time string or `-`.
- `uuid_parse()` return value in `cmd_subvolume_show()` is not checked, so invalid UUID text may become an unintended lookup key.
- `create_one_subvolume()` builds parent directories with fixed `PATH_MAX` buffers and repeated `strcat()`; very long paths depend on prior truncation behavior from `strncpy_null()`.
- `wait_for_subvolume_cleaning()` returns `-errno` after `error_btrfs_util(err)`, but `errno` reliability depends on libbtrfsutil setting it for every error.

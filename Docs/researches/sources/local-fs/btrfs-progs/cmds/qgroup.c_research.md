# File Research: sources/local-fs/btrfs-progs/cmds/qgroup.c

## Purpose

Implements the `btrfs qgroup` command group and the reusable `btrfs_qgroup_query()` helper. It manages quota group creation, deletion, relation changes, listing, filtering, sorting, limits, and stale qgroup cleanup.

## Commands Implemented

- `qgroup assign [--rescan|--no-rescan] <src> <dst> <path>`
- `qgroup remove [--rescan|--no-rescan] <src> <dst> <path>`
- `qgroup create <qgroupid> <path>`
- `qgroup destroy <qgroupid> <path>`
- `qgroup show [options] <path>`
- `qgroup limit [-c] [-e] <size>|none [<qgroupid>] <path>`
- `qgroup clear-stale <path>`

## Core Data Structures

- `struct btrfs_qgroup`
  - In-memory representation of a qgroup.
  - Stores qgroup ID, optional path, stale marker, info item, limit item, parent qgroups, and member qgroups.
  - Embedded rb nodes support lookup, sorted output, and parent traversal.

- `struct btrfs_qgroup_list`
  - Bidirectional relationship entry connecting child and parent qgroups.

- `struct qgroup_lookup`
  - Holds qgroup status flags and rb-tree root for qgroup lookup.

- `struct btrfs_qgroup_filter_set`
  - Dynamic list of filters used by `qgroup show`.

- `struct btrfs_qgroup_comparer_set`
  - Dynamic list of comparers used for multi-key sorting.

## Query and Graph Construction

- `__qgroups_search()` walks the quota tree using the tree-search ioctl and consumes:
  - `BTRFS_QGROUP_STATUS_KEY`
  - `BTRFS_QGROUP_INFO_KEY`
  - `BTRFS_QGROUP_LIMIT_KEY`
  - `BTRFS_QGROUP_RELATION_KEY`

- `get_or_add_qgroup()` creates graph nodes and, for level-0 qgroups, attempts to resolve the corresponding subvolume path and stale status through libbtrfsutil.

- `update_qgroup_info()`, `update_qgroup_limit()`, and `update_qgroup_relation()` populate qgroup accounting, limit, and parent/child data.

- `btrfs_qgroup_query()` searches for one qgroup and fills `struct btrfs_qgroup_stats`; this is declared in `qgroup.h`.

## Output Behavior

`qgroup show` supports classic table output and JSON output.

Table columns include:

- qgroup ID
- referenced bytes
- exclusive bytes
- max referenced limit
- max exclusive limit
- parent qgroups
- child qgroups
- path

Sorting supports:

- `qgroupid`
- `path`
- `rfer`
- `excl`
- `max_rfer`
- `max_excl`

Filters support:

- `-f`: qgroups directly impacting the given path.
- `-F`: all qgroups impacting the given path, including ancestral qgroups.

## Important Behavior

- Qgroup status warnings are printed when quotas are disabled, rescan is running, or accounting is inconsistent.
- `check_qgroup_sysfs_inconsistent()` supplements quota-tree status with sysfs because tree-search status can lag until transaction commit.
- `qgroup assign/remove` can schedule quota rescans when the kernel reports accounting became inconsistent.
- `qgroup limit` accepts `none` as an unlimited size and can limit either referenced or exclusive space.
- `qgroup clear-stale` syncs the filesystem, enumerates qgroups, and deletes stale level-0 qgroups whose subvolume root no longer exists.
- In simple quota mode, non-empty stale qgroups can represent required accounting placeholders and are not deleted.

## External Interfaces

Uses Btrfs quota ioctls:

- `BTRFS_IOC_QGROUP_ASSIGN`
- `BTRFS_IOC_QGROUP_CREATE`
- `BTRFS_IOC_QGROUP_LIMIT`
- quota tree search through shared tree-search helpers

Uses libbtrfsutil for subvolume path/info and filesystem sync, and sysfs helpers for inconsistent/mode status.

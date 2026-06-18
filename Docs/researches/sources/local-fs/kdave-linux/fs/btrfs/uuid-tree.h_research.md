# File Research: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.h

## Purpose

`uuid-tree.h` declares Btrfs UUID tree operations for mapping subvolume UUIDs and received UUIDs to subvolume IDs.

## Public APIs

The header exposes:

- `btrfs_uuid_tree_add()` to add a UUID/type/subid mapping inside a transaction.
- `btrfs_uuid_tree_remove()` to remove a mapping inside a transaction.
- `btrfs_uuid_tree_check_overflow()` to preflight whether another subid can fit under a UUID key.
- `btrfs_uuid_tree_iterate()` to validate and clean UUID tree entries.
- `btrfs_create_uuid_tree()` to create and populate the UUID tree.
- `btrfs_uuid_scan_kthread()` as the worker entry point for initial population.

## Integration Notes

The header forward-declares `struct btrfs_trans_handle` and `struct btrfs_fs_info`, minimizing dependencies. Callers must pass valid UUID item types and manage transactions where required by the add/remove APIs.

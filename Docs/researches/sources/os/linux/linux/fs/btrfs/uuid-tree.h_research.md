# File Research: sources/os/linux/linux/fs/btrfs/uuid-tree.h

## Purpose

`uuid-tree.h` declares the public interface for Btrfs UUID tree management.

## Public API

The header exposes mutation helpers:

- `btrfs_uuid_tree_add()`
- `btrfs_uuid_tree_remove()`

It exposes validation and maintenance helpers:

- `btrfs_uuid_tree_check_overflow()`
- `btrfs_uuid_tree_iterate()`

It exposes creation and asynchronous population hooks:

- `btrfs_create_uuid_tree()`
- `btrfs_uuid_scan_kthread()`

## Filesystem Role

The header is used by Btrfs code that updates root UUID metadata, checks whether UUID-tree items can grow, creates the UUID tree, or kicks/scans the UUID index for consistency.

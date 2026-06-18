# File Research: sources/local-fs/kdave-linux/fs/btrfs/props.h

## Purpose

Header for Btrfs property operations.

## Exports

- `btrfs_props_init()`
- `btrfs_set_prop()`
- `btrfs_validate_prop()`
- `btrfs_ignore_prop()`
- `btrfs_load_inode_props()`
- `btrfs_inode_inherit_props()`

## Dependencies

Forward declares Btrfs inode, path, and transaction-handle types. Includes Linux type and compiler-type headers.

## Role in the System

Provides the property subsystem API used by xattr/inode creation paths without exposing the internal handler table.

# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-checker.h

## Purpose

This header declares the Btrfs tree-checker interface and shared validation status types used by kernel Btrfs code and btrfs-progs-compatible validation paths.

## Key Types

`struct btrfs_tree_parent_check` describes expected parent-derived properties for an extent buffer:
- `owner_root`: expected owner root, or zero to skip.
- `transid`: expected transaction id, or zero to skip. Comments note this should only be skipped by backref-walk-related code.
- `first_key`: expected first key.
- `has_first_key`: whether first-key validation should be performed.
- `level`: expected tree level; should always be set.

`enum btrfs_tree_block_status` gives structured validation outcomes:
- Clean.
- Invalid nritems.
- Invalid parent key.
- Bad key order.
- Invalid level.
- Invalid free space.
- Invalid offsets.
- Invalid block pointer.
- Invalid item.
- Invalid owner.
- Written flag not set.

## Constants

`BTRFS_BLOCK_GROUP_VALID` defines the accepted block group flag mask as type flags, profile flags, and `BTRFS_BLOCK_GROUP_REMAPPED`.

## Exported Functions

- `__btrfs_check_leaf(struct extent_buffer *leaf)`: returns detailed tree block status.
- `__btrfs_check_node(struct extent_buffer *node)`: returns detailed tree block status.
- `btrfs_check_leaf(struct extent_buffer *leaf)`: returns `0` or `-EUCLEAN`.
- `btrfs_check_node(struct extent_buffer *node)`: returns `0` or `-EUCLEAN`.
- `btrfs_check_chunk_valid(...)`: common chunk validation for leaf chunk items and superblock syschunk arrays.
- `btrfs_check_eb_owner(...)`: validates extent buffer owner against expected root owner.
- `btrfs_verify_level_key(...)`: validates extent buffer level and optional first key against parent check metadata.

## Dependencies and Integration

The header forward-declares Btrfs core structures and includes on-disk Btrfs tree definitions. It is consumed by tree read/verification paths and by code that needs chunk validation independent of full leaf validation.

## Research Notes

This header cleanly separates detailed status-returning internal validators from simple errno-returning public wrappers. The `btrfs_tree_parent_check` structure is the key contract for validating that a read tree block matches the parent pointer’s expectations.

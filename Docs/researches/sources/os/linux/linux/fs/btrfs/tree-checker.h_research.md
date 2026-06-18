# File Research: sources/os/linux/linux/fs/btrfs/tree-checker.h

## Purpose

This header declares the public Btrfs tree-checker interface and shared validation status types. It is used by tree read/validation paths and by code that needs parent/owner checks for extent buffers.

## Core Types

`struct btrfs_tree_parent_check` describes expected parent-derived metadata for a tree block:
- `owner_root`: expected owner root, or 0 to skip.
- `transid`: expected transaction id, or 0 to skip.
- `first_key`: expected first key.
- `has_first_key`: whether first-key validation should run.
- `level`: expected tree level.

`enum btrfs_tree_block_status` enumerates detailed validation outcomes:
- Clean block.
- Invalid nritems.
- Invalid parent key.
- Bad key order.
- Invalid level.
- Invalid free space.
- Invalid offsets.
- Invalid block pointer.
- Invalid item.
- Invalid owner.
- Missing written flag.

## Constants

`BTRFS_BLOCK_GROUP_VALID` defines the accepted block group/chunk flag mask:
- Type mask.
- Profile mask.
- Remapped flag.

## Declared APIs

- `__btrfs_check_leaf()`: detailed leaf validation returning `enum btrfs_tree_block_status`.
- `__btrfs_check_node()`: detailed node validation returning `enum btrfs_tree_block_status`.
- `btrfs_check_leaf()`: public leaf validator returning 0 or `-EUCLEAN`.
- `btrfs_check_node()`: public node validator returning 0 or `-EUCLEAN`.
- `btrfs_check_chunk_valid()`: common validator for chunk items and superblock syschunk entries.
- `btrfs_check_eb_owner()`: validates extent buffer owner against expected root owner.
- `btrfs_verify_level_key()`: validates extent buffer level and optional first key against parent expectations.

## Important Invariants

- `level` in `btrfs_tree_parent_check` should always be set.
- `transid` and `first_key` checks may be skipped only in limited contexts such as backref walking.
- The detailed status enum is exported because btrfs-progs wants the same status values.
- The header intentionally forward-declares most Btrfs structs to keep dependencies narrow.

## Research Notes

This header is the compact contract for `tree-checker.c`: callers can either request detailed validation status or the simpler kernel-style 0/error wrappers, and parent checks are bundled into a single structure to avoid ambiguous call signatures.

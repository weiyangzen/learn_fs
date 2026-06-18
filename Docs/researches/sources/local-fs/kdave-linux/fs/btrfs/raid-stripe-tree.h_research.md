# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.h

## Purpose

Header for RAID stripe tree helpers and supported-profile checks.

## Key Definitions

`BTRFS_RST_SUPP_BLOCK_GROUP_MASK` includes supported data profiles:
- DUP
- RAID1 variants
- RAID0
- RAID10

## Exports

- `btrfs_delete_raid_extent()`
- `btrfs_get_raid_extent_offset()`
- `btrfs_insert_raid_extent()`
- `btrfs_insert_one_raid_extent()` under sanity-test builds

## Inline Helpers

- `btrfs_need_stripe_tree_update(fs_info, map_type)`:
  - Requires `RAID_STRIPE_TREE` incompat feature.
  - Only applies to data block groups.
  - Returns true for supported profiles in `BTRFS_RST_SUPP_BLOCK_GROUP_MASK`.
- `btrfs_num_raid_stripes(item_size)`:
  - Derives stride count from item size divided by `sizeof(struct btrfs_raid_stride)`.

## Role in the System

Provides the small public API and profile gating used by write, delete, and logical-to-physical mapping paths for the RAID stripe tree feature.

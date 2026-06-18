# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.h

This header declares the RAID stripe tree API and small helpers for deciding when stripe-tree metadata is needed.

Definitions:
- `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` lists supported RAID/profile bits:
  - DUP
  - RAID1 mask
  - RAID0
  - RAID10

Public API:
- `btrfs_delete_raid_extent()` removes stripe-tree mappings for a logical range.
- `btrfs_get_raid_extent_offset()` resolves logical IO to a stored per-device physical offset and may shorten IO length at stripe extent boundaries.
- `btrfs_insert_raid_extent()` records stripe extents from an ordered extent.
- Under sanity tests, `btrfs_insert_one_raid_extent()` is exported for direct testing.

Inline helpers:
- `btrfs_need_stripe_tree_update()` returns true only when:
  - the filesystem has `RAID_STRIPE_TREE`;
  - the block group type is data;
  - the profile is one of the supported RAID stripe tree profiles.
- `btrfs_num_raid_stripes()` derives the number of strides from the item size.

Role:
- Provides the interface between ordered extent completion, extent deletion, IO mapping, and the stripe-tree implementation.
- Encapsulates feature/profile gating so callers can cheaply skip stripe-tree work when unsupported or unnecessary.

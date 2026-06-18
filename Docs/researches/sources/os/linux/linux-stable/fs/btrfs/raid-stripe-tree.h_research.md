# File Research: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.h

This header declares the RAID stripe tree API and inline helpers.

Definitions:
- `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` lists supported profiles for RAID stripe tree updates:
  - DUP
  - RAID1 variants
  - RAID0
  - RAID10

Public API:
- `btrfs_delete_raid_extent()` deletes a logical range from the stripe tree.
- `btrfs_get_raid_extent_offset()` looks up the physical offset for a logical address, stripe index, and target device stripe.
- `btrfs_insert_raid_extent()` inserts stripe extents associated with an ordered extent.
- Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, `btrfs_insert_one_raid_extent()` is exposed for tests.

Inline helpers:
- `btrfs_need_stripe_tree_update()` returns true only when:
  - the filesystem has the `RAID_STRIPE_TREE` incompat feature,
  - the block group type is data,
  - the profile is in the supported RAID stripe tree mask.
- `btrfs_num_raid_stripes()` derives stride count from item size by dividing by `sizeof(struct btrfs_raid_stride)`.

Dependencies:
- Includes UAPI tree definitions plus Btrfs filesystem and accessor headers because inline helpers inspect block group flags and on-disk stride sizing.

Role in the subsystem:
- Provides the gatekeeping and exported operation surface for RAID stripe tree maintenance and lookup.

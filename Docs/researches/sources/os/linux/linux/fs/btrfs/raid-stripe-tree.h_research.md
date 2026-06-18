# File Research: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.h

This header declares the Btrfs RAID stripe tree API and small inline helpers.

Definitions:
- `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` lists supported profiles: DUP, RAID1 variants, RAID0, and RAID10.

Public API:
- `btrfs_delete_raid_extent()` removes logical ranges from the stripe tree.
- `btrfs_get_raid_extent_offset()` maps logical IO to stripe physical offsets and may shorten length for split IO.
- `btrfs_insert_raid_extent()` inserts stripe records for an ordered extent.
- Under sanity tests, `btrfs_insert_one_raid_extent()` is exported for direct testing.

Inline helpers:
- `btrfs_need_stripe_tree_update()` returns true only when the RAID stripe tree incompat feature is enabled, the block group is data, and the profile is supported.
- `btrfs_num_raid_stripes()` derives stride count from item size.

Role:
- Provides the stripe-tree contract to IO completion, deletion/truncation, mapping, and tests.
- Centralizes feature/profile gating so callers can avoid unnecessary stripe-tree work.

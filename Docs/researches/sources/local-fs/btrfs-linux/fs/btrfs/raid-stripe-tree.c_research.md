# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid-stripe-tree.c

This file implements the Btrfs RAID stripe tree operations. The stripe tree maps logical data extents to per-stripe device IDs and physical offsets for supported RAID profiles when the `RAID_STRIPE_TREE` incompat feature is enabled.

Primary functions:
- `btrfs_delete_raid_extent()` deletes or trims RAID stripe tree entries covering a logical range.
- `btrfs_insert_one_raid_extent()` inserts or updates one RAID stripe extent from a `btrfs_io_context`.
- `btrfs_insert_raid_extent()` inserts all stripe extents attached to an ordered extent and releases their bioc references.
- `btrfs_get_raid_extent_offset()` resolves a logical address and device stripe to the physical offset stored in the stripe tree.

Deletion behavior:
- `btrfs_delete_raid_extent()` first skips work if the feature/root is absent or the target chunk profile does not need stripe-tree updates.
- It searches by logical start and handles overlap cases:
  - deletion range punches a hole inside one stripe extent;
  - deletion trims the tail of an existing extent;
  - deletion trims the front of an existing extent;
  - deletion removes whole stripe extent items.
- `btrfs_partially_delete_raid_extent()` deletes an old item and reinserts a shortened item, adjusting each stride’s physical offset by `frontpad`.
- Hole punching duplicates the right-side item, adjusts right-side physical offsets, then truncates/reinserts the left-side item.
- The search uses `offset = (u64)-1` to land correctly even when the target is the first item on a leaf.

Insertion behavior:
- `btrfs_insert_one_raid_extent()` allocates a variable-sized `struct btrfs_stripe_extent` based on the RAID profile factor.
- It fills each `btrfs_raid_stride` with device ID and physical address from `bioc->stripes`.
- The key is `(logical, BTRFS_RAID_STRIPE_KEY, size)`.
- If insertion returns `-EEXIST`, `update_raid_extent_item()` overwrites the existing item payload.
- Non-recoverable insert/update failures abort the transaction.

Ordered extent integration:
- `btrfs_insert_raid_extent()` is feature-gated on `RAID_STRIPE_TREE`.
- It iterates `ordered_extent->bioc_list`, inserts each recorded stripe extent, then removes and drops each bioc.

Lookup behavior:
- `btrfs_get_raid_extent_offset()` searches the stripe root for an item containing the requested logical address.
- It supports commit-root lookup through `stripe->rst_search_commit_root`, using skip-locking/search-commit-root path flags.
- If the requested logical range crosses the found stripe extent boundary, it shortens `*length` so upper layers split IO at the stripe-tree boundary.
- It selects the stride matching `stripe->dev->devid`; for DUP it also requires the requested stripe index.
- On success it sets `stripe->physical = stride physical + logical offset`.
- On miss it returns `-ENODATA` and emits a debug message outside commit-root search and non-EIO cases.

Dependencies:
- Uses Btrfs item insertion/deletion/search helpers.
- Uses chunk map/profile helpers from `volumes.h`.
- Uses `btrfs_need_stripe_tree_update()` and `btrfs_num_raid_stripes()` from `raid-stripe-tree.h`.
- Uses tracepoints for insert/delete/lookup observability.

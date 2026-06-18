# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid-stripe-tree.c

## Purpose

Implements the Btrfs RAID stripe tree, which maps logical data ranges to per-device physical stripe locations for supported RAID profiles.

## Main Interfaces

- `btrfs_delete_raid_extent(struct btrfs_trans_handle *trans, u64 start, u64 length)`: removes or trims RAID stripe extents overlapping a logical range.
- `btrfs_insert_one_raid_extent(struct btrfs_trans_handle *trans, struct btrfs_io_context *bioc)`: creates one RAID stripe extent item from an IO context.
- `btrfs_insert_raid_extent(struct btrfs_trans_handle *trans, struct btrfs_ordered_extent *ordered_extent)`: inserts all stripe extents attached to an ordered extent and releases their `bioc` references.
- `btrfs_get_raid_extent_offset(...)`: resolves a logical address to a device physical address using the stripe tree.

## Delete Logic

`btrfs_delete_raid_extent()` handles overlap cases carefully:
- No stripe tree feature or no stripe root: no-op.
- Non-testing mode checks the chunk map and skips profiles that do not need stripe tree updates.
- Searches by `objectid=start`, `offset=(u64)-1`, then backs up one slot to find the relevant item.
- Handles:
  - complete item deletion
  - truncating left side
  - truncating right side with physical offset adjustment
  - punching a middle hole by duplicating the item for the right range and truncating the left range
  - ranges spanning multiple stripe extents

`btrfs_partially_delete_raid_extent()` deletes the old item and reinserts a trimmed copy, adjusting each stride’s physical address by `frontpad`.

## Insert Logic

`btrfs_insert_one_raid_extent()`:
- Allocates a variable-sized `btrfs_stripe_extent` based on profile factor.
- Copies devid and physical offsets from `bioc->stripes[]`.
- Inserts key `(logical, BTRFS_RAID_STRIPE_KEY, size)`.
- If the item already exists, overwrites it via `update_raid_extent_item()`.
- Aborts the transaction on insertion/update failures.

`btrfs_insert_raid_extent()` processes all `bioc` records linked to an ordered extent and releases them afterward.

## Lookup Logic

`btrfs_get_raid_extent_offset()`:
- Searches the stripe tree for the stripe extent containing `logical`.
- Supports commit-root lookup through `stripe->rst_search_commit_root`.
- Reduces `*length` if the requested range crosses a stripe extent boundary, forcing higher layers to split the bio.
- Finds the stride matching the requested device id.
- For DUP profiles, also matches the requested stripe index.
- Returns `-ENODATA` when no suitable stripe mapping exists.

## Dependencies

Uses Btrfs tree search/update helpers, transaction APIs, chunk maps, ordered extent IO contexts, tracepoints, and `raid-stripe-tree.h`.

## Error Handling

- Allocation failures return `-ENOMEM`.
- Missing chunk map returns `-EINVAL`.
- Missing stripe mapping returns `-ENODATA`.
- Insert/update failures abort the transaction where appropriate.
- Lookup logs debug diagnostics except for expected commit-root/EIO cases.

## Role in the System

This file maintains the persistent logical-to-physical stripe mapping required by the RAID stripe tree incompat feature for supported data block group profiles.

# File Research: sources/os/linux/linux-stable/fs/btrfs/raid-stripe-tree.c

This file implements management of Btrfs RAID stripe tree items. The RAID stripe tree stores logical stripe extents as `BTRFS_RAID_STRIPE_KEY` items whose key objectid is logical start and key offset is length; payload strides map each stripe to device id and physical address.

Delete path:
- `btrfs_delete_raid_extent()` removes or trims stripe extents covering a logical range.
- It is a no-op if the RAID stripe tree incompat feature or `stripe_root` is absent.
- Outside tests, it first checks the chunk map and skips deletion if the map type does not require stripe tree updates.
- It searches using `(objectid=start, type=RAID_STRIPE_KEY, offset=-1)` and backs up one slot to find the relevant preceding/overlapping extent.
- It handles all overlap shapes:
  - deletion range in the middle of an item: duplicates a right item, adjusts right physical offsets, then truncates left.
  - deletion range at the end of an item: truncates left.
  - deletion range at the front of an item: recreates the remaining right part with physical offsets advanced by the front padding.
  - full item coverage: deletes the item.
  - multi-item deletion: loops, advancing `start` and `length`.
- `btrfs_partially_delete_raid_extent()` performs delete-and-reinsert for a trimmed item, copying all strides and adding `frontpad` to physical offsets.

Insert/update path:
- `btrfs_insert_one_raid_extent()` builds a `struct btrfs_stripe_extent` sized by the RAID profile factor from a `btrfs_io_context`.
- It fills each stride with device id and physical address from the bioc stripes.
- It inserts a `BTRFS_RAID_STRIPE_KEY` item keyed by logical start and bioc size.
- If the item already exists, it updates the existing payload through `update_raid_extent_item()`.
- On insert/update failure it aborts the transaction.
- `btrfs_insert_raid_extent()` iterates all biocs attached to an ordered extent, inserts each one, then drains the ordered extent’s `bioc_list` and drops references.

Lookup path:
- `btrfs_get_raid_extent_offset()` maps a logical address to the physical address for a target `btrfs_io_stripe`.
- It can search the commit root without locking when `stripe->rst_search_commit_root` is set.
- It locates the containing stripe extent, shortens `*length` if the request crosses a physically non-contiguous stripe extent boundary, and scans strides for the requested device id.
- For DUP profiles, it also requires `stripe_index` to match the stride index.
- On missing data it returns `-ENODATA` and logs debug output unless searching the commit root.

Key dependencies:
- Stripe tree root from `fs_info->stripe_root`.
- Btrfs item insertion/deletion/search helpers.
- `btrfs_io_context`, `btrfs_io_stripe`, ordered extents, and chunk maps from the volume/mapping layer.
- `btrfs_num_raid_stripes()` and update gating from `raid-stripe-tree.h`.

Role in the subsystem:
- Maintains the persistent logical-to-physical stripe mapping needed by the RAID stripe tree feature for supported data RAID profiles.

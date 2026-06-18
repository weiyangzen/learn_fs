# File Research: sources/os/linux/linux/fs/btrfs/raid-stripe-tree.c

This file implements Btrfs RAID stripe tree operations. The stripe tree maps logical file extents to per-stripe physical device offsets for supported RAID profiles.

Primary functions:
- `btrfs_delete_raid_extent()` deletes a logical range from the RAID stripe tree.
- `btrfs_insert_one_raid_extent()` inserts or updates one stripe extent from a `btrfs_io_context`.
- `btrfs_insert_raid_extent()` inserts all stripe extents attached to an ordered extent and releases their `bioc` references.
- `btrfs_get_raid_extent_offset()` looks up the physical offset for a logical range, device, profile, and stripe index.

Deletion behavior:
- `btrfs_delete_raid_extent()` no-ops when the RAID stripe tree feature/root is absent or the chunk profile does not require stripe-tree updates.
- It searches for stripe extents overlapping `[start, start + length)`.
- It handles all overlap shapes:
  - whole-item deletion,
  - deleting the right tail of an item,
  - deleting the left head of an item,
  - punching a hole by duplicating the item for the right side and truncating the left side.
- `btrfs_partially_delete_raid_extent()` rebuilds an item with adjusted logical start/length and physical stride offsets.

Insertion behavior:
- `btrfs_insert_one_raid_extent()` builds a variable-sized `struct btrfs_stripe_extent` with one stride per RAID factor.
- The key is `(logical, BTRFS_RAID_STRIPE_KEY, size)`.
- If insertion finds an existing item, it updates the item payload.
- Insert/update failures abort the transaction where appropriate.
- `btrfs_insert_raid_extent()` iterates `ordered_extent->bioc_list`, inserts each mapping, then removes and puts all `bioc` entries.

Lookup behavior:
- `btrfs_get_raid_extent_offset()` searches the stripe root, optionally through the commit root with skipped locking.
- It backs up one slot when exact search misses so a containing extent can be found.
- If the requested logical range crosses a stripe extent boundary, it shortens `*length` so the caller can split IO.
- It selects the stride matching the requested device ID, and for DUP profiles also matches `stripe_index`.
- Returns `-ENODATA` when no matching stripe extent/device is found.

Dependencies:
- Uses Btrfs tree search/insert/delete helpers.
- Uses `btrfs_io_context`, ordered extents, chunk maps, and volume/profile helpers.
- Emits tracepoints for insert, delete, and lookup.

Risk notes:
- Range deletion is sensitive to off-by-one and item-split behavior.
- Physical stride offsets must be adjusted consistently when logical ranges are truncated or split.
- Lookup may mutate requested length to enforce physically continuous IO boundaries.

# File Research: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.c

Implements the Btrfs UUID tree, an index from subvolume UUID or received UUID to subvolume root ids, plus creation, scanning, validation, and stale-entry cleanup.

Key entry points:
- `btrfs_uuid_tree_add()` adds a root id to the UUID item for a given UUID/type pair.
- `btrfs_uuid_tree_remove()` removes a root id from a UUID item and deletes the whole item when it was the last id.
- `btrfs_uuid_tree_check_overflow()` checks whether adding another root id would exceed maximum leaf item capacity.
- `btrfs_uuid_tree_iterate()` walks UUID-tree items and removes stale subvolume UUID entries.
- `btrfs_uuid_scan_kthread()` scans root items and populates the UUID tree after creation.
- `btrfs_create_uuid_tree()` creates the UUID tree root, commits it, and starts the rescan kthread.

Core mechanics:
- `btrfs_uuid_to_key()` maps a 16-byte UUID into a Btrfs key by storing the first 8 bytes in `objectid`, the key type in `type`, and the second 8 bytes in `offset`, using unaligned little-endian loads.
- UUID tree item payloads are packed arrays of little-endian `u64` subvolume/root ids.
- `btrfs_uuid_tree_lookup()` searches for a UUID/type key and scans the item payload for a specific subid.
- Adding first tries lookup to avoid duplicates. New UUID/type pairs insert an item; existing pairs extend the item and append the new subid.
- Removal searches with transaction intent, finds the matching subid payload entry, memmoves later ids over it, and truncates the item, or deletes the item when only one id existed.
- Iteration reconstructs UUID bytes from key objectid/offset, validates referenced subvolume roots, and deletes entries whose root is gone or whose UUID no longer matches the root item.
- The scan kthread walks tree-root `BTRFS_ROOT_ITEM_KEY` items, filters live subvolume roots, and writes non-empty `uuid` and `received_uuid` values to the UUID tree in small transactions.

Important invariants:
- UUID item sizes must be aligned to `sizeof(u64)`; unaligned sizes are warned about and treated as invalid/skipped.
- The UUID tree root must exist for add/remove/check operations; missing roots trigger `WARN_ON_ONCE()` and `-EINVAL`.
- Only `BTRFS_UUID_KEY_SUBVOL` and `BTRFS_UUID_KEY_RECEIVED_SUBVOL` are semantically validated by stale-entry checks.
- Overflow prevention must account for `struct btrfs_item` plus current payload plus one `u64` within the leaf data size.
- The rescan semaphore is released when the scan kthread exits, and `BTRFS_FS_UPDATE_UUID_TREE_GEN` is set only after successful non-closing scans.

Filesystem relevance:
- The UUID tree is a metadata index for subvolume identity and received-subvolume identity. It supports efficient lookup and maintenance of UUID-to-root-id mappings used by ioctl/subvolume workflows.

Notable risks:
- Corrupt item lengths are tolerated with warnings but can leave entries skipped rather than repaired in place.
- The iteration cleanup restarts searches after removals, which is correct but can be expensive if many stale entries exist.
- Scan population uses separate transactions while walking root items; error handling must carefully release paths and end transactions.

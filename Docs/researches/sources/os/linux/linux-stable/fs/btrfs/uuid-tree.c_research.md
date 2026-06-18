# File Research: sources/os/linux/linux-stable/fs/btrfs/uuid-tree.c

## Scope

This file implements Btrfs UUID tree maintenance. The UUID tree maps subvolume UUIDs and received UUIDs to subvolume/root IDs, supports add/remove/overflow checks, validates existing entries, scans roots to populate a new UUID tree, and creates the UUID tree when needed.

## Public And Internal APIs Covered

- Public operations: `btrfs_uuid_tree_add()`, `btrfs_uuid_tree_remove()`, `btrfs_uuid_tree_check_overflow()`, `btrfs_uuid_tree_iterate()`, `btrfs_uuid_scan_kthread()`, `btrfs_create_uuid_tree()`.
- Internal helpers: `btrfs_uuid_to_key()`, `btrfs_uuid_tree_lookup()`, `btrfs_uuid_iter_rem()`, `btrfs_check_uuid_tree_entry()`.

## Control Flow And Behavior

- UUID keys are derived by splitting the 16-byte UUID into little-endian `objectid` and `offset`, with key type indicating subvolume UUID or received-subvolume UUID.
- Add first checks for an existing UUID/subid pair. If absent, it inserts a new item or extends an existing item and appends the little-endian subvolume ID.
- Remove searches the UUID item, finds the matching subid, deletes the whole item if it was the only entry, or compacts and truncates the item otherwise.
- Overflow check verifies whether one more `u64` subid can fit in the leaf item.
- Iteration walks UUID tree items, validates subvolume UUID mappings against the referenced root item, and removes stale entries in their own short transactions.
- The scan kthread walks the tree root for live root items, skips deleted/unreferenced roots, and inserts non-empty UUID and received UUID mappings into the UUID tree.
- Creating the UUID tree starts a transaction, creates the dedicated UUID tree root, commits it, then starts the rescan kthread under `uuid_tree_rescan_sem`.

## State And Data Structures

- UUID tree items store a variable-length array of little-endian `u64` subvolume IDs.
- Valid item sizes must be aligned to `sizeof(u64)`.
- Root items supply `uuid`, `received_uuid`, root refs, and root IDs.
- `fs_info->uuid_root`, `tree_root`, `uuid_tree_rescan_sem`, and `BTRFS_FS_UPDATE_UUID_TREE_GEN` are central state.

## Dependencies

- Btrfs transaction, path, search, item insert/extend/truncate/delete, root lookup, and tree creation APIs.
- Linux kthread, UUID/unaligned helpers, and scheduler rescheduling.

## Risks And Invariants

- UUID item sizes must remain `u64` aligned; malformed sizes are warned and treated as lookup/removal failures or skipped during iteration.
- The UUID tree can contain multiple subids for one UUID key, so add/remove must preserve compact array layout.
- Iteration releases the path before modifying the tree and restarts search after removals to avoid stale path state.
- The scan kthread must stop cleanly on filesystem closing and always release the rescan semaphore.

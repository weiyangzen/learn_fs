# File Research: sources/local-fs/kdave-linux/fs/btrfs/uuid-tree.c

## Purpose

`uuid-tree.c` manages Btrfs' UUID tree, a filesystem tree that maps subvolume UUIDs and received UUIDs to subvolume/root IDs. It supports lookup, insertion, removal, overflow checking, consistency cleanup, initial tree creation, and asynchronous scanning to populate the UUID tree.

This tree accelerates subvolume discovery by UUID and tracks both normal subvolume UUIDs and received-subvolume UUIDs used by send/receive workflows.

## Key Format

`btrfs_uuid_to_key()` converts a 16-byte UUID into a Btrfs key:

- `objectid`: little-endian first 8 bytes of UUID.
- `offset`: little-endian second 8 bytes of UUID.
- `type`: UUID item type, such as `BTRFS_UUID_KEY_SUBVOL` or `BTRFS_UUID_KEY_RECEIVED_SUBVOL`.

Each UUID tree item payload is a packed list of little-endian `u64` subvolume IDs. Multiple subvolumes can share the same UUID item key, so the payload can contain more than one subid.

## Lookup, Add, Remove

`btrfs_uuid_tree_lookup()` searches the UUID root for a key and scans the item payload for a given subid. It returns `0` when found, `-ENOENT` when not found, and negative errors for failures. It validates that the item size is aligned to `sizeof(u64)`.

`btrfs_uuid_tree_add()` first calls lookup to avoid duplicates. It inserts a new item when the UUID key is absent, or extends an existing item and appends the new subid when the key exists.

`btrfs_uuid_tree_remove()` searches with a transaction, finds the matching subid, and either deletes the whole item when it contains only one subid or compacts the payload with `memmove_extent_buffer()` and truncates the item.

## Capacity Check

`btrfs_uuid_tree_check_overflow()` determines whether another `u64` subid can be appended to an existing UUID item without exceeding leaf item capacity. If no item exists, insertion is allowed. If adding one `u64` plus item metadata would exceed `BTRFS_LEAF_DATA_SIZE()`, it returns `-EOVERFLOW`.

This is a preventive check for UUID collisions or repeated entries that would make a single item too large.

## Consistency Iteration

`btrfs_uuid_tree_iterate()` walks the UUID tree and validates entries for subvolume and received-subvolume UUID item types.

For each subid in a UUID item, it calls `btrfs_check_uuid_tree_entry()`:

- If the subvolume root does not exist, the entry is stale.
- For `BTRFS_UUID_KEY_SUBVOL`, the UUID must match `root_item.uuid`.
- For `BTRFS_UUID_KEY_RECEIVED_SUBVOL`, the UUID must match `root_item.received_uuid`.

Stale entries are removed by `btrfs_uuid_iter_rem()` in a small transaction, then the walk restarts from the adjusted key. The iterator also exits with `-EINTR` when the filesystem is closing.

## Initial Scan Thread

`btrfs_uuid_scan_kthread()` scans `fs_info->tree_root` for `BTRFS_ROOT_ITEM_KEY` items. For each live subvolume root item with a non-empty UUID or received UUID, it starts a transaction on `fs_info->uuid_root` and adds the appropriate UUID tree entries.

Important filtering rules:

- It skips non-root-item keys.
- It skips objectids outside the valid free/subvolume range, except `BTRFS_FS_TREE_OBJECTID`.
- It skips root items too small to contain `struct btrfs_root_item`.
- It skips roots with zero root refs.
- It checks `btrfs_fs_closing()` and yields with `cond_resched()`.

On successful completion that was not due to closing, it sets `BTRFS_FS_UPDATE_UUID_TREE_GEN`. It always releases `uuid_tree_rescan_sem` before exiting.

## UUID Tree Creation

`btrfs_create_uuid_tree()` starts a transaction on the tree root, creates `BTRFS_UUID_TREE_OBJECTID`, stores it in `fs_info->uuid_root`, commits the transaction, then launches `btrfs_uuid_scan_kthread()` to populate the new tree.

It holds `uuid_tree_rescan_sem` across kthread startup. If thread creation fails, it releases the semaphore and returns the error.

## Dependencies

The file depends on Btrfs transaction, root-tree, path/search, item manipulation, and extent-buffer APIs from `ctree.h`, `transaction.h`, `disk-io.h`, `fs.h`, `accessors.h`, and `ioctl.h`. It uses Linux `kthread`, UUID helpers, and unaligned little-endian accessors.

## Invariants And Risks

UUID item payloads must be `u64` aligned; malformed item sizes are warned and treated as not found/skipped. Add/remove operations assume UUID root existence and warn on unexpected insertion failures.

The consistency walk is intentionally restart-heavy after removals, prioritizing correctness over scan efficiency because stale UUID entries should be exceptional.

Risk areas are transaction sizing, path release/restart after item mutation, UUID item overflow, and shutdown interaction in the scan thread.

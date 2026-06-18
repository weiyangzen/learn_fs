# File Research: sources/os/linux/linux/fs/btrfs/uuid-tree.c

## Purpose

`uuid-tree.c` implements Btrfs' UUID tree support. The UUID tree indexes subvolume UUIDs and received UUIDs so the filesystem can find subvolumes by UUID and keep that index consistent with the root tree.

Each UUID key maps one UUID and UUID-key type to a variable-length array of subvolume/root IDs stored as little-endian `u64` values.

## Key Format

`btrfs_uuid_to_key()` converts a 16-byte UUID to a Btrfs key:

- key type is the UUID item type, such as `BTRFS_UUID_KEY_SUBVOL` or `BTRFS_UUID_KEY_RECEIVED_SUBVOL`.
- objectid is the first little-endian 64 bits of the UUID.
- offset is the second little-endian 64 bits of the UUID.

The item payload is an array of subvolume IDs associated with that UUID.

## Lookup, Add, Remove

`btrfs_uuid_tree_lookup()` searches the UUID root for a UUID/type key and scans the item payload for a specific subvolume ID. It returns 0 when found, `-ENOENT` when absent, and negative errors for failures. It validates that item size is aligned to `sizeof(u64)` and warns on illegal sizes.

`btrfs_uuid_tree_add()` first calls lookup to avoid duplicate subvolume IDs. If the item does not exist, it inserts a new one with one `u64`. If the key exists, it extends the item and appends the new subvolume ID.

`btrfs_uuid_tree_remove()` searches the item under transaction context, scans for the matching subvolume ID, deletes the whole item if it was the only entry, or compacts the remaining payload with `memmove_extent_buffer()` and truncates the item.

`btrfs_uuid_tree_check_overflow()` checks whether appending one more `u64` to a UUID item would exceed the leaf data size. It returns `-EOVERFLOW` when the item cannot be extended.

## Consistency Checking

`btrfs_check_uuid_tree_entry()` validates a UUID-tree entry against the referenced subvolume root. For supported UUID item types, it loads the subvolume root by ID:

- missing root returns a positive value so the caller removes the stale UUID-tree entry.
- a UUID mismatch also returns a positive value.
- other lookup errors propagate as negative errors.

`btrfs_uuid_iter_rem()` wraps removal of one stale entry in a one-item transaction.

`btrfs_uuid_tree_iterate()` scans the UUID tree forward and validates every subvolume and received-subvolume UUID entry. Stale entries are removed, then the scan restarts from the current key. The function checks for filesystem shutdown and returns `-EINTR` if closing.

## UUID Tree Creation and Rescan

`btrfs_create_uuid_tree()` creates the UUID tree root in a transaction, commits it, then starts the `btrfs-uuid` kernel thread to populate the new tree from existing root items. It protects the rescan with `uuid_tree_rescan_sem`.

`btrfs_uuid_scan_kthread()` walks the tree root for `BTRFS_ROOT_ITEM_KEY` items representing live subvolumes. For each root item with a non-empty normal UUID or received UUID, it starts or reuses a transaction with two reserved items and adds corresponding UUID tree entries. It skips roots with zero refs and invalid objectid ranges.

On successful completion, if the filesystem is not closing, the thread sets `BTRFS_FS_UPDATE_UUID_TREE_GEN`. It always releases the rescan semaphore before returning.

## Error Handling

The file consistently treats malformed UUID item sizes as warnings and generally returns `-ENOENT` for those specific bad entries. Transaction start, path allocation, search, insert, extend, delete, and commit failures propagate as negative errors. Creation aborts the transaction if creating the tree root fails.

## Filesystem Role

The UUID tree is an auxiliary metadata index. It does not own subvolume lifetime; instead, it mirrors UUID fields from root items and provides repair/rescan paths to remove stale mappings and build the index when needed.

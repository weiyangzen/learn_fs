# File Research: sources/os/linux/linux/fs/btrfs/dir-item.c

This file implements Btrfs directory item and xattr item insertion, lookup, collision detection, name matching, and deletion. Btrfs stores name-hashed directory and xattr items that may contain multiple packed entries when names collide on the hash.

Insertion:
- `insert_with_overflow()` inserts an empty item for a key or, on `-EEXIST`, checks for an exact name match and extends the existing item to append another packed entry.
- `btrfs_insert_xattr_item()` validates xattr size, builds a `BTRFS_XATTR_ITEM_KEY` using `btrfs_name_hash()`, inserts/extends the item, initializes the embedded `btrfs_dir_item`, and copies name/data payloads.
- `btrfs_insert_dir_item()` inserts the name-hash `BTRFS_DIR_ITEM_KEY` entry and then queues the directory index entry through `btrfs_insert_delayed_dir_index()` unless operating on the tree root.
- Encrypted directories mark the file type with `BTRFS_FT_ENCRYPTED`.

Lookup:
- `btrfs_lookup_match_dir()` wraps `btrfs_search_slot()` with mode-dependent insertion/deletion parameters and calls `btrfs_match_dir_item_name()`.
- `btrfs_lookup_dir_item()` searches the hash-keyed directory item and returns NULL for not found.
- `btrfs_lookup_dir_index_item()` searches a specific `BTRFS_DIR_INDEX_KEY` by index and name.
- `btrfs_search_dir_index_item()` scans directory index items from offset zero until it finds a matching name or leaves the directory index key range.
- `btrfs_lookup_xattr()` searches hash-keyed xattr items.

Collision and packed-entry handling:
- `btrfs_check_dir_item_collision()` detects exact name existence and checks whether a hash-collision entry can fit into the existing leaf item; if not, it returns `-EOVERFLOW`.
- `btrfs_match_dir_item_name()` walks all packed `btrfs_dir_item` records inside a single item, comparing name length and name bytes from the extent buffer.
- `btrfs_delete_one_dir_name()` deletes either the whole item when it contains only one entry or compacts the item by memmoving later packed entries over the deleted entry and truncating the item.

Cross-file relationships:
- Delayed directory index insertion is implemented in `delayed-inode.c`.
- The public declarations and `btrfs_name_hash()` inline helper live in `dir-item.h`.
- Callers depend on transaction, ctree, extent buffer, fscrypt string, and accessor helpers.

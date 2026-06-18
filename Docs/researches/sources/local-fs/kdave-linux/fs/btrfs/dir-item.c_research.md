# File Research: sources/local-fs/kdave-linux/fs/btrfs/dir-item.c

This file implements Btrfs directory item and xattr item insertion, lookup, collision detection, matching, and deletion. It handles Btrfs’ packed directory item format, where multiple names with the same hash may share one tree item.

Insertion:
- `insert_with_overflow()` attempts `btrfs_insert_empty_item()`.
- On `-EEXIST`, it checks for an exact name collision inside the packed item; if absent, it extends the item and returns a pointer to the newly appended subitem.
- `btrfs_insert_xattr_item()` inserts an xattr item keyed by `BTRFS_XATTR_ITEM_KEY` and name hash, writes empty location key, flags `BTRFS_FT_XATTR`, name length, data length, transaction id, name, and value.
- It enforces `BTRFS_MAX_XATTR_SIZE()`.
- `btrfs_insert_dir_item()` inserts the name-hash `BTRFS_DIR_ITEM_KEY` entry and then, except in the tree root, queues the secondary `BTRFS_DIR_INDEX_KEY` insertion through delayed inode code.
- Encrypted directories OR in `BTRFS_FT_ENCRYPTED`.

Lookup:
- `btrfs_lookup_match_dir()` does a tree search with mode-dependent insert length and COW flag, then scans the packed item for a matching name.
- `btrfs_lookup_dir_item()` looks up by directory objectid and name hash.
- `btrfs_lookup_dir_index_item()` looks up by directory objectid and explicit index offset.
- `btrfs_search_dir_index_item()` iterates all directory index items for a directory and returns the first matching name.
- `btrfs_lookup_xattr()` looks up xattr packed items by name hash.

Collision detection:
- `btrfs_check_dir_item_collision()` verifies whether inserting a name would collide exactly, overflow the leaf, or fit into an existing hash bucket.
- Returns:
  - `0` when safe.
  - `-EEXIST` for exact name match.
  - `-EOVERFLOW` when the packed item cannot fit another entry.
  - Other negative errors from lookup.

Packed item scanning:
- `btrfs_match_dir_item_name()` walks subitems inside the current tree item using each subitem’s name and data lengths.
- It compares name length and `memcmp_extent_buffer()` content.

Deletion:
- `btrfs_delete_one_dir_name()` deletes one packed dir/xattr subitem.
- If the subitem is the whole tree item, it deletes the item.
- Otherwise it memmoves the following bytes over the removed subitem and truncates the item.

Cross-file relationships:
- Secondary directory index insert/delete batching is in `delayed-inode.c`.
- Hashing helper is declared inline in `dir-item.h`.
- Uses Btrfs accessors for endian-safe item field reads/writes.

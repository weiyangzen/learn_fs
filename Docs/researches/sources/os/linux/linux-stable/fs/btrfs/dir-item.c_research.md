# File Research: sources/os/linux/linux-stable/fs/btrfs/dir-item.c

This file implements Btrfs directory item and xattr item insertion, lookup, collision checking, matching, and deletion. Directory names and xattrs are keyed by CRC32C name hash and can store multiple colliding names inside one btree item.

Insertion:
- `insert_with_overflow()` inserts an empty item for a hash key or extends an existing item on hash collision. It rejects exact duplicate names and returns a pointer to the newly reserved sub-item area.
- `btrfs_insert_xattr_item()` inserts an xattr as a `BTRFS_XATTR_ITEM_KEY`, validates maximum xattr size, initializes the dir-item payload, and writes name/data bytes.
- `btrfs_insert_dir_item()` inserts the name-hash directory item and queues the directory index item through `btrfs_insert_delayed_dir_index()`, except for the tree root. Encrypted directories mark the file type with `BTRFS_FT_ENCRYPTED`.

Lookup:
- `btrfs_lookup_match_dir()` searches a btree key and then scans the item payload for the requested name.
- `btrfs_lookup_dir_item()` looks up a directory entry by name hash and name.
- `btrfs_lookup_dir_index_item()` looks up a directory index entry by index and name.
- `btrfs_search_dir_index_item()` scans directory index keys for a matching name.
- `btrfs_lookup_xattr()` looks up xattr items by name hash and name.

Collision handling:
- `btrfs_check_dir_item_collision()` checks whether a hash key already has the exact name, has enough room for another colliding name, or would overflow a leaf.
- Return meanings:
  - `0`: safe to insert.
  - `-EEXIST`: exact name already exists.
  - `-EOVERFLOW`: hash collision item lacks room.
  - Other negative errors from search/allocation.

Matching:
- `btrfs_match_dir_item_name()` walks all packed `btrfs_dir_item` entries inside a single btree item and compares name lengths and name bytes using extent-buffer accessors.

Deletion:
- `btrfs_delete_one_dir_name()` deletes a packed dir-item entry. If it is the only sub-item, it deletes the btree item; otherwise it memmoves later sub-items down and truncates the item.

Data layout:
- Directory and xattr entries use `struct btrfs_dir_item` followed by name bytes and optional data bytes.
- Name hash is `crc32c((u32)~1, name, len)` via the header helper.

Role in Btrfs:
This file handles the low-level packed directory/xattr item format. It works with delayed inode code for directory index insertion while directly managing name-hash items in the subvolume tree.

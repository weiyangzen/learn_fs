# File Research: sources/local-fs/kdave-linux/fs/btrfs/dir-item.h

This header declares directory/xattr item helpers and defines the Btrfs name hash helper.

Exported operations:
- Collision and insertion:
  - `btrfs_check_dir_item_collision()`
  - `btrfs_insert_dir_item()`
  - `btrfs_insert_xattr_item()`
- Lookup:
  - `btrfs_lookup_dir_item()`
  - `btrfs_lookup_dir_index_item()`
  - `btrfs_search_dir_index_item()`
  - `btrfs_lookup_xattr()`
- Packed item helper:
  - `btrfs_match_dir_item_name()`
- Deletion:
  - `btrfs_delete_one_dir_name()`

Hashing:
- `btrfs_name_hash()` returns `crc32c((u32)~1, name, len)`.
- Directory and xattr primary keys use this hash in their key offset, with packed collision handling in `dir-item.c`.

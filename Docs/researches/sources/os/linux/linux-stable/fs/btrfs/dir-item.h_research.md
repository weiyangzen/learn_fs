# File Research: sources/os/linux/linux-stable/fs/btrfs/dir-item.h

This header declares Btrfs directory item and xattr item helpers.

Public API:
- Directory insertion and collision:
  - `btrfs_check_dir_item_collision()`
  - `btrfs_insert_dir_item()`
- Directory lookup:
  - `btrfs_lookup_dir_item()`
  - `btrfs_lookup_dir_index_item()`
  - `btrfs_search_dir_index_item()`
- Directory deletion/matching:
  - `btrfs_delete_one_dir_name()`
  - `btrfs_match_dir_item_name()`
- Xattr insertion/lookup:
  - `btrfs_insert_xattr_item()`
  - `btrfs_lookup_xattr()`

Hash helper:
- `btrfs_name_hash()` computes CRC32C with seed `~1`, returning the hash used as the key offset for directory and xattr name-hash items.

Role in Btrfs:
The header exposes the packed dir-item/xattr-item primitives used by inode, directory, rename, xattr, and delayed directory-index code.

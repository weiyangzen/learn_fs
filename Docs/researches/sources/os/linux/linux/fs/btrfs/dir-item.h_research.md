# File Research: sources/os/linux/linux/fs/btrfs/dir-item.h

This header declares Btrfs directory item and xattr item helpers and defines the directory name hash helper.

Exported operations:
- Directory insertion: `btrfs_insert_dir_item()`.
- Directory lookup: `btrfs_lookup_dir_item()`, `btrfs_lookup_dir_index_item()`, and `btrfs_search_dir_index_item()`.
- Collision detection: `btrfs_check_dir_item_collision()`.
- Name matching and deletion inside packed items: `btrfs_match_dir_item_name()` and `btrfs_delete_one_dir_name()`.
- Xattr item insertion and lookup: `btrfs_insert_xattr_item()` and `btrfs_lookup_xattr()`.

Hashing:
- `btrfs_name_hash()` computes a CRC32C hash seeded with `~1`, used for hash-keyed `BTRFS_DIR_ITEM_KEY` and `BTRFS_XATTR_ITEM_KEY` offsets.

Design notes:
- The API accepts `struct fscrypt_str` for directory names so encrypted-name handling can be passed through the same lookup/insert paths.
- `mod` parameters on lookup declarations encode read-only, modification, or deletion slot-search behavior.

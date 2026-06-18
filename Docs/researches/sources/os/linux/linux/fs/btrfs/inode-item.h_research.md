# File Research: sources/os/linux/linux/fs/btrfs/inode-item.h

## Purpose
Declares inode item/reference helper APIs and `struct btrfs_truncate_control`, used by inode metadata code and free-space-cache inode truncation.

## Key Definitions
- `BTRFS_NEED_TRUNCATE_BLOCK`: positive return value indicating caller must truncate the final block separately.
- `struct btrfs_truncate_control`
  - Inputs:
    - `inode`
    - `new_size`
    - `ino`
    - `min_type`
    - `skip_ref_updates`
    - `clear_extent_range`
  - Outputs:
    - `extents_found`
    - `last_size`
    - `sub_bytes`

## Inline Helpers
- `btrfs_inode_combine_flags()` combines mutable and read-only inode flags into the u64 on-disk inode-item representation.
- `btrfs_inode_split_flags()` splits the u64 on-disk representation back into two u32 values.
- `btrfs_extref_hash()` computes the extended inode-ref key offset using CRC32C over parent objectid and name.

## Public API
- Truncation:
  - `btrfs_truncate_inode_items()`
- Inode ref insertion/deletion:
  - `btrfs_insert_inode_ref()`
  - `btrfs_del_inode_ref()`
- Inode item creation/lookup:
  - `btrfs_insert_empty_inode()`
  - `btrfs_lookup_inode()`
- Extended ref lookup and name matching:
  - `btrfs_lookup_inode_extref()`
  - `btrfs_find_name_in_backref()`
  - `btrfs_find_name_in_ext_backref()`

## Design Notes
The header isolates inode item mutation contracts from the rest of Btrfs. The free-space cache code depends on this header for creating cache inodes and truncating their extent data safely inside transactions.

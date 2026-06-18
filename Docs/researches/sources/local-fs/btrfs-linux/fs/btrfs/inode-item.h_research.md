# File Research: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.h

## Summary
Declares Btrfs inode item/reference helpers and defines the truncate-control structure used by inode item truncation.

## Main Contents
- `BTRFS_NEED_TRUNCATE_BLOCK` return value for truncation paths that must truncate the final block separately.
- `struct btrfs_truncate_control` input/output state for `btrfs_truncate_inode_items()`.
- Inline helpers to combine and split persisted inode flags and read-only inode flags.
- `btrfs_extref_hash()` helper for extended inode reference item keys.
- Declarations for inode ref search, insert, delete, lookup, empty inode insertion, and truncation.

## Key Interfaces
The main public entry points are `btrfs_truncate_inode_items()`, `btrfs_insert_inode_ref()`, `btrfs_del_inode_ref()`, `btrfs_insert_empty_inode()`, `btrfs_lookup_inode()`, `btrfs_lookup_inode_extref()`, `btrfs_find_name_in_backref()`, and `btrfs_find_name_in_ext_backref()`.

## Important Details
`btrfs_truncate_control` separates inputs from outputs in comments. Callers provide inode/objectid, target size, minimum key type, and behavior flags; the truncate helper returns extent count, last size reached, and byte accounting.

Inode item flags are stored on disk as one 64-bit value but split in memory into two 32-bit fields. `btrfs_inode_combine_flags()` and `btrfs_inode_split_flags()` encode that boundary.

`btrfs_extref_hash()` uses CRC32C seeded by parent objectid over the name bytes, producing the key offset for extended inode refs.

## Risks
The truncate control allows `inode` to be `NULL` only when `clear_extent_range` is false. Callers must satisfy that contract because truncation may otherwise dereference the inode while clearing extent state.

Extended-ref hashes can collide, so users of the hash must still compare parent objectid and name inside the item.

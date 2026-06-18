# File Research: sources/os/linux/linux-stable/fs/btrfs/inode-item.h

## Purpose

Declares inode-item and inode-reference helper APIs implemented by `inode-item.c`, plus the truncate-control structure used by generic inode truncation callers including the free-space cache code.

## Key Definitions

`BTRFS_NEED_TRUNCATE_BLOCK` is a positive return value indicating the caller must truncate the last block separately. `struct btrfs_truncate_control` carries truncate inputs (`inode`, `new_size`, `ino`, `min_type`, `skip_ref_updates`, `clear_extent_range`) and outputs (`extents_found`, `last_size`, `sub_bytes`).

## Inline Helpers

`btrfs_inode_combine_flags()` and `btrfs_inode_split_flags()` convert between on-disk 64-bit inode flags and in-memory writable/read-only flag halves. `btrfs_extref_hash()` computes the key offset for extended inode refs using CRC32C over parent objectid and name.

## Public API Surface

The header declares truncate, inode-ref insert/delete, empty inode insertion, inode lookup, extended-ref lookup, and name-search helpers for normal and extended backrefs.

## Integration Notes

The free-space cache code uses this interface when creating hidden cache inodes and when truncating cache inode file extent items. Other Btrfs directories/inode code use the same helpers for link count/reference management and file truncation.

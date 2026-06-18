# File Research: sources/local-fs/kdave-linux/fs/btrfs/inode-item.h

This header declares inode item/reference helpers and the truncate-control structure used by Btrfs inode item deletion and truncation paths.

Key definitions:
- `BTRFS_NEED_TRUNCATE_BLOCK` is the positive return code indicating the caller must truncate the final block separately.
- `struct btrfs_truncate_control` carries truncation inputs and outputs: inode pointer, target size, inode number, minimum key type, skip-ref-update flag, clear-extent-range flag, extents found, last size, and bytes to subtract.

Inline helpers:
- `btrfs_inode_combine_flags()` packs mutable and read-only inode flags into the u64 on-disk inode item representation.
- `btrfs_inode_split_flags()` unpacks the u64 inode item flags into separate in-memory flag words.
- `btrfs_extref_hash()` computes the extended inode ref key offset using CRC32C over parent objectid and name bytes.

Public API:
- `btrfs_truncate_inode_items()` removes inode-associated items and truncates file extent items according to a `btrfs_truncate_control`.
- `btrfs_insert_inode_ref()` and `btrfs_del_inode_ref()` manage normal and extended inode refs.
- `btrfs_insert_empty_inode()` creates an empty inode item.
- `btrfs_lookup_inode()` searches for inode/root items.
- `btrfs_lookup_inode_extref()` locates an extended inode ref.
- `btrfs_find_name_in_backref()` and `btrfs_find_name_in_ext_backref()` scan packed ref records inside leaf items.

This header is used by normal inode/directory code and by the free-space cache inode creation/truncation path.

# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_extents.h

Defines ext4 extent on-disk structures used by the ext2fs driver. It includes extent magic, cache status values, `struct ext4_extent`, `struct ext4_extent_index`, `struct ext4_extent_header`, `struct ext4_extent_cache`, and `struct ext4_extent_path`.

The exported API is limited to extent cache check/store and extent path lookup. This reinforces that extents are supported for mapping existing files, while classic ext2 block allocation remains separate.

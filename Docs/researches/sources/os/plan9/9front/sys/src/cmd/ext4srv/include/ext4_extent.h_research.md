# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_extent.h

Extent tree accessor and API header for extent-based file block mapping.

Key behavior:
- Defines `ext4_extent_path`, the traversal path entry used for lookup, insertion, splitting, and truncation.
- Defines macros for unwritten extent state, max written/unwritten lengths, first/last extent/index entry, extent tail offset, in-range checks, and max blocks.
- Provides inline endian-safe accessors for extent logical block, length, physical block, index logical/physical block, and extent header fields.
- `ext4_extent_tree_init` initializes an inode-stored root extent header and marks the inode reference dirty.
- Declares `ext4_extent_get_blocks` for lookup/allocation/conversion and `ext4_extent_remove_space` for truncation/freeing.

Notable dependencies:
- Includes `ext4_inode.h`; implemented by `ext4_extent.c`.
- On-disk extent structs are defined in `ext4_types.h`.

Research notes:
- `EXT4_EXT_SET_UNWRITTEN` and `EXT4_EXT_SET_WRITTEN` directly mutate the little-endian `nblocks` field with masks; this assumes the mask expression matches on-disk endian representation.
- Inline initialization computes inode-root capacity from the fixed inode `blocks[]` area.

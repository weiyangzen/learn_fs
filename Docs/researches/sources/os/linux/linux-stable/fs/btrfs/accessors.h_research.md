# File Research: sources/os/linux/linux-stable/fs/btrfs/accessors.h

## Summary
Declares and generates Btrfs typed accessors for on-disk structures in extent buffers and stack copies.

## Main Responsibilities
- Defines macros for extent-buffer, header, and stack get/set helpers.
- Provides endian-safe accessors for device, chunk, block group, inode, extent, node, item, dir, root, superblock, file extent, qgroup, dev replace, verity, and remap structures.
- Provides key conversion helpers between disk and CPU representations.
- Provides item pointer and item offset helpers.

## Important Behavior
`BTRFS_SETGET_FUNCS` and variants enforce field-size expectations with `static_assert()`. Little-endian builds optimize key conversion by `memcpy()`, while other builds convert objectid/offset explicitly.

Header accessors use the first extent-buffer folio and `offset_in_page(eb->start)`. Item helpers compute leaf item array offsets and data-area pointers, forming the standard typed bridge from B-tree slots to on-disk records.

## Risks
This header is a broad metadata ABI layer. Field size mismatches, wrong endian conversions, or pointer offset errors would affect many independent Btrfs subsystems. Some setters add invariants, such as sector alignment for device total bytes.

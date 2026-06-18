# File Research: sources/os/linux/linux/fs/btrfs/accessors.h

Purpose: Declares and generates Btrfs typed accessors for serialized on-disk structures in extent buffers and in-memory stack copies.

Core macro families:
- `DECLARE_BTRFS_SETGET_BITS`: declares generic scalar extent-buffer accessors.
- `BTRFS_SETGET_FUNCS`: generates extent-buffer field accessors.
- `BTRFS_SETGET_HEADER_FUNCS`: optimized metadata header accessors from the first extent-buffer folio.
- `BTRFS_SETGET_STACK_FUNCS`: generates accessors for materialized disk-format structs in memory.
- `read_eb_member` and `write_eb_member`: copy non-scalar members between extent buffers and memory.

Major accessor groups:
- Device, chunk, stripe, block group, block group v2, and free-space metadata.
- Inode refs, inode extrefs, inode items, timespecs, RAID stride records, and dev extents.
- Extent items, tree block info, extent data refs, shared data refs, owner refs, and inline refs.
- B-tree nodes, leaf items, item keys, item offsets/sizes, directory items, root refs, and free-space headers.
- Disk key conversion helpers, with optimized little-endian memcpy paths and explicit conversion for other architectures.
- Metadata headers, root items, root backups, balance items, superblock fields, file extents, qgroups, device replace, verity descriptors, and remap items.

Important helpers:
- `btrfs_extent_inline_ref_size()` maps inline ref types to serialized sizes and returns zero for unknown types.
- `btrfs_node_blockptr()`, `btrfs_node_ptr_generation()`, and node key helpers access internal node slots.
- `btrfs_item_ptr()` and `btrfs_item_ptr_offset()` cast into the leaf data area.
- `btrfs_header_flag()`, `btrfs_set_header_flag()`, and `btrfs_clear_header_flag()` manipulate header flags.
- `btrfs_is_leaf()` checks header level.
- `btrfs_set_device_total_bytes()` warns if device size is not sectorsize-aligned.

Invariants:
- Generated field accessors use `static_assert` to ensure the requested integer width matches the on-disk field size.
- Header accessors assume the metadata header is reachable in the first folio at `offset_in_page(eb->start)`.
- Pointer-shaped values are logical offsets into an extent buffer, not normal kernel pointers.

Risk notes: This header underpins most Btrfs metadata code. It intentionally provides fast typed wrappers over serialized disk structures, so callers still must supply valid slots, item types, and extent buffers.

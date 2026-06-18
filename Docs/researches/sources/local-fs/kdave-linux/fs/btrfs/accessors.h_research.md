# File Research: sources/local-fs/kdave-linux/fs/btrfs/accessors.h

Purpose: Declares and generates the typed accessor layer for Btrfs on-disk structures, covering extent-buffer fields, stack/on-memory copies, headers, keys, items, superblocks, qgroups, device replace, verity descriptors, remap items, and many disk-format records.

Core macro families:
- `DECLARE_BTRFS_SETGET_BITS`: declares generic `btrfs_get_*` and `btrfs_set_*`.
- `BTRFS_SETGET_FUNCS`: generates extent-buffer accessors for fields inside on-disk structs.
- `BTRFS_SETGET_HEADER_FUNCS`: optimized header accessors using the first extent-buffer folio.
- `BTRFS_SETGET_STACK_FUNCS`: stack/object accessors for already materialized disk-format structs.
- `read_eb_member` and `write_eb_member`: copy non-scalar struct members between extent buffers and memory.

Major accessor groups:
- Device and chunk metadata: `btrfs_device_*`, `btrfs_chunk_*`, stripe helpers and UUID offsets.
- Block groups and free-space info: classic and v2 block group fields, free-space counts and flags.
- Inode refs/items/timespecs: inode metadata, references, extended references, uid/gid/mode/flags, timestamps.
- Extent records: extent item refs/generation/flags, tree block info, extent data refs, shared data refs, owner refs, inline ref type/offset/size.
- Tree nodes and leaf items: node block pointers, node generations, node keys, item offsets/sizes, item keys, item data pointers.
- Directory and root refs: dir item fields, file type conversion helpers, root ref fields.
- Key conversion: optimized little-endian `memcpy` path and explicit endian conversion path for other architectures.
- Headers/root/superblock: header fields, root item and backup fields, superblock fields including remap root fields.
- File extents and qgroups: file extent disk/ram/encoding fields; qgroup status/info/limit fields.
- Device replace, verity, remap-tree: accessor coverage for newer feature records.

Important helpers:
- `btrfs_extent_inline_ref_size()` maps inline ref type to its serialized size and returns zero for unknown types.
- `btrfs_is_leaf()` checks header level.
- `btrfs_header_flag`, `btrfs_set_header_flag`, and `btrfs_clear_header_flag` manipulate header flags.
- `btrfs_item_ptr` and `btrfs_item_ptr_offset` cast into the data region of a leaf.

Invariants and compile-time checks: Generated field accessors use `static_assert` to ensure the requested integer width matches the on-disk field size. The device total-bytes setter warns when the value is not sectorsize-aligned.

Integration: This header is used throughout Btrfs metadata code and is directly depended on by `accessors.c`, `backref.c`, tree checking, disk I/O, extent tree, inode/item code, and superblock handling.

Risk notes: The macros intentionally trade abstraction for speed and type consistency. Because many helpers return pointer-shaped offsets into extent buffers, callers must supply valid slots and item types; corruption detection is mostly in callers and tree-checker paths.

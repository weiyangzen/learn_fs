# File Research: sources/local-fs/btrfs-linux/fs/btrfs/accessors.h

Large inline accessor header for Btrfs on-disk structures.

Key points:
- Defines generic accessor macros:
  - `BTRFS_SETGET_FUNCS()` for extent-buffer backed structures.
  - `BTRFS_SETGET_HEADER_FUNCS()` for extent-buffer header fields.
  - `BTRFS_SETGET_STACK_FUNCS()` for stack-resident on-disk structs.
- Declares `btrfs_get/set_8/16/32/64()` implemented in `accessors.c`.
- Provides read/write member helpers using `read_extent_buffer()` and `write_extent_buffer()`.
- Supplies little-endian optimized key conversion for `__LITTLE_ENDIAN`; big-endian builds perform explicit conversion.
- Covers accessors for device items, chunks, stripes, block groups, free-space info, inode refs, inode items, timespecs, raid strides, dev extents, extent items, inline refs, node pointers, leaf items, directory items, root refs, headers, root items, root backups, balance items, superblock fields, file extent items, qgroups, device replace items, verity descriptor items, and remap items.
- Includes helper pointer calculations such as `btrfs_item_nr_offset()`, `btrfs_item_ptr()`, `btrfs_stripe_nr()`, and UUID field offset helpers.
- `btrfs_extent_inline_ref_size()` maps inline-ref key type to the encoded size consumed in extent items.
- Header accessors assume the Btrfs tree header is in the first extent-buffer folio at `offset_in_page(eb->start)`.

Role in system:
- Provides type-checked, endian-correct access to nearly all Btrfs disk-format structures.
- This file is a core compatibility boundary between in-memory code and the stable on-disk format.

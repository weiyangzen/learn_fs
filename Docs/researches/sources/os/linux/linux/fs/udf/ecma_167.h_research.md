# File Research: sources/os/linux/linux/fs/udf/ecma_167.h

## Purpose
Defines packed ECMA-167 revision 3 on-disk data structures and constants used by the UDF filesystem.

## Main Contents
- Character set, d-string, timestamp, entity identifier structures.
- Volume Structure Descriptor constants and structs.
- Volume/partition descriptors: primary volume descriptor, anchor volume descriptor pointer, logical volume descriptor, partition descriptors/maps, unallocated space descriptor, terminating descriptor, logical volume integrity descriptor.
- Addressing/allocation structs:
  - `extent_ad`
  - `lb_addr` / `kernel_lb_addr`
  - `short_ad`
  - `long_ad` / `kernel_long_ad`
  - `ext_ad` / `kernel_ext_ad`
- File set and file metadata descriptors:
  - `fileSetDesc`
  - `fileIdentDesc`
  - `icbtag`
  - `fileEntry`
  - `extendedFileEntry`
  - allocation extent, indirect, terminal, unallocated-space, bitmap, partition integrity entries.
- Permission, file type, ICB flag, extent type, extended attribute, and descriptor tag constants.

## Important Design Points
- This header is the UDF media format contract; most structs are `__packed` and little-endian annotated.
- It separates some disk structs from in-core analogs, e.g. `kernel_lb_addr`, `kernel_long_ad`, `kernel_ext_ad`.
- Extent type is stored in the high bits of extent length via `EXT_TYPE_MASK`; usable length is `EXT_LENGTH_MASK`.
- File Entry and Extended File Entry layouts are both supported.

## Cross-File Relationships
- Used throughout UDF source, especially `inode.c`, `directory.c`, `balloc.c`, and `ialloc.c`.
- `directory.c` validates and rewrites `fileIdentDesc`.
- `inode.c` decodes/encodes `fileEntry`, `extendedFileEntry`, `icbtag`, device extended attributes, and allocation descriptors.
- `balloc.c` uses space bitmap and unallocated space entry descriptors.

## Risks / Review Notes
- Because this mirrors a standard and on-disk format, changes must be treated as compatibility-sensitive.
- Some identifiers reflect ECMA/UDF terminology and are intentionally not Linux-style abstractions.

# File Research: sources/os/bsd/netbsd-src/sys/fs/hfs/libhfs.h

## Purpose
Defines the HFS/HFS+ on-disk data model, constants, callbacks, global state, and public parser APIs used by `libhfs.c` and the kernel HFS wrapper.

## Main Contents
- Volume signatures, volume attribute bits, B-tree node kinds, B-tree header flags, special CNIDs, catalog record kinds, journal flags, fork types, key comparison types, key-length bounds, and hardlink magic values.
- HFS+ on-disk types: Unicode strings, CNIDs, extent records, forks, volume header, B-tree node/header records, catalog keys, extent keys, BSD metadata, file/folder records, thread records, journal info/header.
- Plain HFS master directory block structures used to locate embedded HFS+ volumes in HFS wrappers.
- `hfs_volume` stores parsed volume header, catalog/extents headers, key size fields, volume name, key comparator, journal metadata, embedded offset, readonly state, and callback data.
- `hfs_catalog_keyed_record_t` represents catalog leaf records or index child pointers.
- `hfs_callback_args` and `hfs_callbacks` define the host-provided allocation, I/O, open, close, and error-reporting hooks.
- Declares global callbacks and global casefolding table.
- Declares high-level lookup/listing/journal/hardlink APIs, low-level structure readers, key constructors, extent readers, comparators, and callback wrappers.

## Dependencies
Includes NetBSD endian/param/mount/types headers and, outside the kernel, libc headers for file, stdarg, stdint, stdio, allocation, and unistd.

## Risks and Notes
The header defines `max` and `min` macros unconditionally, which can collide with other local definitions. Many structs mirror packed disk formats but are decoded through explicit readers rather than direct casting. The callback interface is global, not per-volume, while `hfs_volume.cbdata` carries per-volume data. The API returns mixed conventions: some functions return 0 on success, others return byte counts, CNIDs, or count values, so callers must track each contract carefully.

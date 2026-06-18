# File Research: sources/os/bsd/freebsd-src/sys/fs/udf/ecma167-udf.h

Packed ECMA-167/UDF on-disk format definition header.

Key responsibilities:
- Defines descriptor tag IDs for volume, partition, logical volume, file set, file identifier, and file entry descriptors.
- Defines packed media structures: descriptor tags, logical block addresses, extent/allocation descriptors, character sets, timestamps, entity IDs, ICB tags, anchor descriptors, volume descriptors, partition maps, sparing tables, partition descriptors, file set descriptors, FIDs, file entries, and path components.
- Defines UDF constants for partition map sizes, descriptor sizes, file-character flags, ICB flags, permission masks, and path component types.
- Provides `union dscrptr` and allocation descriptor helper macros `GETICB` and `GETICBLEN`.

Dependencies:
- Requires FreeBSD fixed-width integer types, endian conversion users, and `__packed`.
- Consumed by UDF mount parsing, vnode lookup, block mapping, symlink parsing, and directory iteration code.

Notable risks:
- These structures are disk ABI; packing, field type, or size changes would break UDF media parsing.
- Several definitions contain trailing flexible data areas, so callers must validate descriptor and buffer lengths before using variable fields.
- The implementation supports only a subset of structures described here, especially around partition map and allocation descriptor variants.

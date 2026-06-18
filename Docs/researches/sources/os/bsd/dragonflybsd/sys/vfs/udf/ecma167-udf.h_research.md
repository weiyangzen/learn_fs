# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/ecma167-udf.h

Packed on-disk ECMA-167/UDF descriptor layout header.

Key responsibilities:
- Defines UDF descriptor tag identifiers for primary volume, anchor, volume, implementation volume, partition, logical volume, unallocated space, terminator, integrity, file set, file identifier, and file entry descriptors.
- Defines packed media-format structures used by mount and vnode code: descriptor tags, logical block addresses, extent descriptors, short/long/extended allocation descriptors, character-set specs, timestamps, entity identifiers, ICB tags, anchor pointers, volume descriptors, partition maps, sparing tables, partition descriptors, file set descriptors, file identifier descriptors, and file entries.
- Defines key UDF constants such as `UDF_REGID_ID_SIZE`, `UDF_PMAP_SIZE`, `UDF_FID_SIZE`, `UDF_FENTRY_SIZE`, file-character flags, ICB permission flags, and file-entry permission masks.
- Provides `union dscrptr` for treating a descriptor buffer as one of the known UDF descriptor formats.
- Provides allocation descriptor helper macros `GETICB` and `GETICBLEN`.

Dependencies:
- Requires fixed-width integer types and DragonFly's `__packed` annotation from included kernel headers.
- Consumed by UDF mount parsing and vnode block-mapping code.

Notable risks:
- Structure layout is media ABI; padding, field width, or packing changes would break disk parsing.
- Several structures use flexible one-element tail arrays, so consumers must validate descriptor lengths before copying variable data.
- Comments and implementation only cover a subset of UDF variants; type 2 virtual/sparable maps are described, but runtime support is limited.

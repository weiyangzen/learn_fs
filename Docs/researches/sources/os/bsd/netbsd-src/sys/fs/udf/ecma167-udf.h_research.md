# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/ecma167-udf.h

Read completely: 840 lines.

This is the packed on-media ECMA-167/UDF structure definition header. It defines volume recognition descriptors, descriptor tags, logical block addresses, allocation descriptors, character sets, path components, timestamps, entity identifiers, ICB tags and file types, anchors, volume descriptors, partition maps, sparing tables, VAT structures, space bitmaps, partition descriptors, logical volume integrity descriptors, file set descriptors, file identifier descriptors, extended attributes, file entries, extended file entries, indirect entries, allocation extent descriptors, and a `union dscrptr` overlay for descriptor parsing.

The header also defines key constants for tag ids, extent flags and length masks, UDF ICB allocation formats, file type ids, path component ids, partition flags, file identifier flags, permission masks, and descriptor fixed sizes.

Important interactions: included by `udf.h` and UDF implementation files that parse or construct disk descriptors. All structures are `__packed` to match the media format.

Security/reliability notes: this header has no executable logic but is a critical trust boundary for disk parsing. Many structures use flexible one-element trailing arrays, so consumers must validate descriptor lengths and CRC/tag fields before indexing variable payloads.

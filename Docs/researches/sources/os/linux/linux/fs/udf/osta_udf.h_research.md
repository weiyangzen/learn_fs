# File Research: sources/os/linux/linux/fs/udf/osta_udf.h

Purpose: OSTA UDF 2.60 constants and packed on-disk structure definitions.

Key contents:
- Defines OSTA CS0 character set identifiers.
- Defines UDF entity identifier strings for Linux implementation, compliant domain, VAT, sparable, metadata, allocation tables, system streams, Mac/OS2/NT/UNIX extensions, and other UDF-defined IDs.
- Defines identifier suffix structures: domain, UDF, implementation, and application suffixes.
- Defines logical volume integrity implementation-use and implementation-use volume descriptor payloads.
- Defines type 2 partition maps: virtual, sparable, metadata.
- Defines VAT 2.0 structure and metadata/sparing table structures.
- Defines UDF file type constants for VAT, realtime, metadata main/mirror/bitmap.
- Defines extended attribute payload structures and OS class/identifier constants.

Integration:
- Included by `udfdecl.h`, so most UDF source files use these constants indirectly.
- Parsed heavily by `super.c` during logical volume, partition map, metadata, VAT, sparable, and LVID loading.

Risks and invariants:
- Structures are packed and represent disk layout; field order and endian annotations are contract-critical.
- Identifier string matching controls partition-map interpretation and read/write compatibility decisions.

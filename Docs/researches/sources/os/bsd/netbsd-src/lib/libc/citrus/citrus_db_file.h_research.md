# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_file.h

On-disk structure definitions for Citrus compiled DB files.

Key contents:
- Documents layout: header, entry directory, key table, data table.
- Defines `_CITRUS_DB_MAGIC_SIZE`, `_CITRUS_DB_HEADER_SIZE`, and packed header record.
- Defines packed entry record with hash, next offset, key offset/size, and data offset/size.
- Defines `_CITRUS_DB_ENTRY_SIZE` as 24.

All multi-byte fields are interpreted by reader/writer code as big-endian/network order.

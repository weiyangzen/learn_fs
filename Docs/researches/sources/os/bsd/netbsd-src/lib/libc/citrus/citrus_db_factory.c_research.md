# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_db_factory.c

Builder/serializer for Citrus compiled database files.

Key behavior:
- `_citrus_db_factory_create/free` manage a queue of entries and aggregate key/data sizes.
- Add helpers accept raw regions, strings, and 8/16/32-bit integer values encoded in network byte order.
- `_citrus_db_factory_calc_size` computes a 16-byte-aligned serialized size.
- `_citrus_db_factory_serialize` builds a fixed-size hash directory, resolves collisions with linked entry chains, writes header/entry records, and copies key/data tables.

Format details:
- Header stores magic, entry count, and entry offset.
- Entry records store hash value, next offset, key offset/size, and data offset/size.
- Data records are padded to 16-byte alignment.

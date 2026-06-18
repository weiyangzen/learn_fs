# File Research: sources/virtualization/nbdkit/filters/lzip/lzip.c

Implements the nbdkit lzip decompression filter. It is readonly and supports random reads by indexing lzip members and caching decompressed blocks.

Configuration accepts `lzip-max-block` defaulting to 512 MiB and `lzip-max-depth` defaulting to 8 cache blocks. Each connection opens the upstream plugin readonly, creates a block cache, and initializes `lzipfile` metadata in prepare.

`lzip_prepare()` opens and validates the lzip file and rejects archives whose largest uncompressed member exceeds `lzip-max-block`. Reads first probe the cache by offset; on miss they call `lzipfile_read_block()`, then cache the full decompressed member.

Large requests may span multiple members, handled recursively. The filter disables writes and extents, advertises cache emulation and multi-conn consistency, and serializes requests.

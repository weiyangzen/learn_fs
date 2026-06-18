# File Research: sources/virtualization/nbdkit/filters/indexed-gzip/indexed_gzip.c

Implements the `indexed-gzip` filter. It provides random reads over gzip/deflate streams using a persisted zran index rather than eagerly expanding the whole image.

Configuration requires `gzip-index-path=<PATH>` and optionally accepts `gzip-index-span=<SIZE>`, defaulting to 1 MiB. `indexed_gzip_prepare()` caches the upstream compressed size, loads an existing index with `deflate_index_deserialize()`, or builds one through `ig_deflate_index_build()` and serializes it to the configured path.

The filter is readonly, disables extents, advertises cache emulation and multi-conn consistency, and reports the uncompressed size from `h->index->length`. `indexed_gzip_pread()` calls `ig_deflate_index_extract()` under a global mutex because the index owns a reusable `z_stream`.

The index file format is native binary serialization from `zran.c`; it is not portable across incompatible ABI/endianness layouts.


## sources/storage-engines/wiredtiger/ext/compressors/snappy/snappy_compress.c

Purpose: implements the WiredTiger Snappy compressor and stores the exact compressed byte count required by Snappy decompression.

Important APIs/functions: `SNAPPY_COMPRESSOR` stores the extension API. `SNAPPY_PREFIX` is an eight-byte little-endian compressed-length prefix. `snappy_compression` compresses after the prefix, succeeds only if output plus prefix is smaller than source, writes the prefix, and sets `compression_failed` otherwise. `snappy_decompression` reads and byte-swaps the prefix as needed, validates it against `src_len`, calls `snappy_uncompress`, and returns the produced length. `snappy_error` maps `snappy_status` to extension errors.

State and persistence: persisted blocks are prefix plus Snappy stream. Compressor allocation is per connection and freed on terminate. Risks: prefix load/store uses direct `uint64_t *` casts, which can be sensitive to alignment on strict platforms; decompression depends on prefix integrity; Snappy status errors are converted to `WT_ERROR`. Tests should cover endian behavior, corrupt/truncated prefixes, incompressible data, invalid Snappy payloads, and builtin vs loadable init symbols.

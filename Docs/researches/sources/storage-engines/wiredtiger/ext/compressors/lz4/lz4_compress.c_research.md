
## sources/storage-engines/wiredtiger/ext/compressors/lz4/lz4_compress.c

Purpose: implements WiredTiger's LZ4 compressor extension and preserves backward compatibility for old raw-compression objects.

Important APIs/types/functions: `LZ4_COMPRESSOR` stores extension API state. `LZ4_PREFIX` is a 16-byte little-endian header containing true compressed length, true uncompressed length, useful decompressed length, and reserved zero. Big-endian builds byte-swap with `lz4_prefix_swap`. `lz4_compress` writes compressed data after the prefix and only succeeds when compressed output plus prefix is smaller than source. `lz4_decompress` validates stored size, optionally uses `scr_alloc` as a bounce buffer for legacy raw-compression cases, and verifies decoded bytes equal `useful_len`. `lz_add_compressor` registers both `lz4` and `lz4-noraw`.

State and persistence: compressed blocks persist an LZ4 raw block plus the prefix. The compressor object is per connection and freed on terminate. Risks: prefix corruption must be caught before decompression; the legacy bounce-buffer path can allocate `prefix.uncompressed_len`; size casts to `int` follow library ABI limits; `lz4-noraw` is compatibility surface. Test signals include endian-prefix tests, corrupt prefix lengths, truncated input, bounce-buffer legacy objects, incompressible data marking `compression_failed`, and both registered names.

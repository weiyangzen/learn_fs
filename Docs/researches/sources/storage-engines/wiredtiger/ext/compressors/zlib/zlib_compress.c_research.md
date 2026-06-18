
## sources/storage-engines/wiredtiger/ext/compressors/zlib/zlib_compress.c

Purpose: implements WiredTiger's zlib compressor extension with optional `compression_level` configuration.

Important APIs/types/functions: `ZLIB_COMPRESSOR` stores extension API and compression level. `ZLIB_OPAQUE` lets zlib callbacks allocate/free scratch memory through WiredTiger `scr_alloc` and `scr_free`. `zlib_compress` initializes a z_stream, runs `deflate(..., Z_FINISH)`, marks compression failure if the stream does not finish, then ends the stream. `zlib_decompress` inflates until completion and reports `total_out`. `zlib_init_config` accepts levels 0 through 9. `zlib_extension_init` registers both `zlib` and `zlib-noraw`.

State and persistence: no custom prefix; persisted bytes are zlib stream output. Compressor state is per connection. Risks: `pre_size` is NULL, so sizing relies on WiredTiger's generic handling; `avail_in/out` are cast to `uint32_t`; decompression loops until `inflate` stops and trusts zlib to catch corruption; raw-compat registration expands API surface. Tests should cover all valid compression levels, invalid level rejection, custom allocator failure, truncated streams, incompressible data, and both compressor names.

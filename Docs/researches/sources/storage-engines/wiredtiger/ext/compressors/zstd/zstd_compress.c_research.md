
## sources/storage-engines/wiredtiger/ext/compressors/zstd/zstd_compress.c

Purpose: implements WiredTiger's Zstandard compressor with pooled compression/decompression contexts.

Important APIs/types/functions: `ZSTD_CONTEXT_POOL` holds a spinlock and free list of `ZSTD_CONTEXT` wrappers. `ZSTD_COMPRESSOR` stores compression level plus separate pools for `ZSTD_CCtx` and `ZSTD_DCtx`. `zstd_compress` gets a context if available, writes compressed data after an eight-byte little-endian length prefix, and succeeds only when smaller than input. `zstd_decompress` validates the stored length and uses a pooled or temporary decompression context. `zstd_pre_size` returns `ZSTD_compressBound + prefix`. `zstd_init_context_pool` creates 50 contexts by default; terminate frees pools and destroys spinlocks.

State and persistence: persisted blocks are prefix plus zstd payload. Runtime state includes two context pools guarded by WiredTiger spinlocks. Risks: `zstd_extension_init` does not check return values from `zstd_init_context_pool`, so allocation/context-creation failures can leave null pools that later code assumes exist; partial pool-init failures can leak objects; compression level is accepted without range validation; direct prefix `uint64_t *` access may be alignment-sensitive. Tests should include context-pool exhaustion, fallback path when no context is free, pool init failure, corrupt prefixes, high/low compression levels, and terminate under active-use constraints.

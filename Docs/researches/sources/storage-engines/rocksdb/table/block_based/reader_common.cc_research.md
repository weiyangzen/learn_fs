# sources/storage-engines/rocksdb/table/block_based/reader_common.cc

Purpose: implements small shared utilities for block-based table readers: forced cache release and checksum verification for physical blocks.

Important APIs/types/functions: `ForceReleaseCachedEntry(void*, void*)` casts arguments to `Cache` and `Cache::Handle` and releases with `erase_if_last_ref=true`. `VerifyBlockChecksum` checks the block trailer checksum using footer checksum settings, file name, block offset, and `BlockType`.

Control flow: checksum verification asserts the RocksDB block trailer size of five bytes, computes the checksum over block bytes plus compression type byte, decodes the stored checksum, removes the context checksum modifier based on footer base context and offset, compares, and returns either OK or a detailed corruption status. For CRC32c, it unmasks stored and computed values for diagnostics.

State and persistence: no persistent state is written. It consumes persisted trailer bytes and footer checksum metadata. `PERF_TIMER_GUARD(block_checksum_time)` records verification time in perf context.

Dependencies/integration: depends on `Footer`, checksum helpers in `util/crc32c`/`util/coding`, block type stringification, and perf context. `BlockFetcher::ProcessTrailerIfPresent` calls `VerifyBlockChecksum` when `ReadOptions::verify_checksums` is enabled.

Risks and test signals: the function assumes `data` includes a complete trailer after `block_size`, so callers must ensure full block-plus-trailer reads. Context checksum subtraction is subtle and affects diagnostic values. Block fetcher tests exercise successful reads and compression type handling, but this subset does not include explicit checksum mismatch tests.

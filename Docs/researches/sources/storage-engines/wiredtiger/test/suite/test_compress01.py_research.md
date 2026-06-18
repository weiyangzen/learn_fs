<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compress01.py

Purpose: smoke-tests block compression across file and table data sources with multiple compressor extensions.

Important APIs and control flow: scenario matrices combine URI type (`file:` or `table:`) with compressors (`nop`, `lz4`, `snappy`, `zlib`, `zstd`, `iaa`, plus compatibility names). `conn_extensions()` requests compressor extension loading and skips when missing. `test_compress()` creates a string-key/string-value object with `block_compressor`, inserts 100 mixed large/small values, reopens the connection to force disk reads, then searches every key and verifies exact values.

State, persistence, and dependencies: state lives in compressed WiredTiger pages on disk. The reopen boundary is central because it clears cached values and validates decompression from persisted pages. Dependencies are `wttest`, `make_scenarios`, extension loading, and the cursor insert/search API.

Integration points: covers compressor extension registration, table/file creation config, block manager compression/decompression, and compatibility with old raw-compression variants.

Risks and test signals: unavailable compressors skip scenarios, so coverage depends on build configuration. The signal is full value equality after reopen; failures point to compressor configuration, extension loading, page write/read, or value-boundary handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress01.py -->

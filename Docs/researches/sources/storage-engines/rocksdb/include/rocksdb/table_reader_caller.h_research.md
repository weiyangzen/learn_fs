# Research: sources/storage-engines/rocksdb/include/rocksdb/table_reader_caller.h

- **Purpose:** Defines `TableReaderCaller`, a compact enum tagging who requested table-reader/block-cache access for tracing and analysis.
- **Important APIs/types/functions:** Values include user operations (`kUserGet`, `kUserMultiGet`, `kUserIterator`, `kUserApproximateSize`, `kUserVerifyChecksum`), tools and internal paths (`kSSTDumpTool`, `kExternalSSTIngestion`, `kRepair`, `kPrefetch`, `kCompaction`, `kCompactionRefill`, `kFlush`, `kSSTFileReader`), `kUncategorized`, and `kMaxBlockCacheLookupCaller`.
- **Control flow:** Callers pass one of these tags into table-reader/cache lookup paths; tracing and analysis aggregate hits/misses or block activity by caller.
- **State and persistence:** The enum has no state and is not a durable file format, but trace records/logs may store or interpret its values.
- **Dependencies:** Only depends on the RocksDB namespace header.
- **Integration points:** Used by block cache tracing, table reader benchmarks/tests, compaction refill, flush verification, SST dump, ingestion, and user read paths.
- **Risks:** New table-reader call paths that use `kUncategorized` lose attribution. Consumers must keep arrays sized to `kMaxBlockCacheLookupCaller`.
- **Test signals:** Block cache trace tests should assert expected caller tags for Get, MultiGet, iterator, compaction, flush, ingestion, and SST dump paths.

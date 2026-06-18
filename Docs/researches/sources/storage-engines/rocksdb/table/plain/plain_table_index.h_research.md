<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_index.h

Purpose: Declares plain table index reader and builder classes and documents the persistent index format.

Important APIs and types: `PlainTableIndex` exposes `GetOffset()`, `InitFromRawData()`, `GetSubIndexBasePtrAndUpperBound()`, size/count accessors, `IndexSearchResult`, and constants `kMaxFileSize`, `kSubIndexMask`, and `kOffsetLen`. `PlainTableIndexBuilder` exposes `AddKeyPrefix()`, `Finish()`, `GetTotalSize()`, and static block name `kPlainTableIndexBlock`. Nested `IndexRecordList` groups temporary records in fixed-size arrays.

Control flow: Readers use the primary bucket table to either jump directly to a file offset, report no prefix, or decode a second-level subindex for binary search. Builders collect offsets, allocate index/subindex space in an arena, and serialize it into a block stored in the plain SST.

State and persistence: `PlainTableIndex` points into raw persisted index bytes; it does not own them. Builder state tracks prefix counts, previous prefix, current sparseness state, index/subindex sizes, hash table ratio, huge-page allocation size, and an arena-owned output buffer.

Dependencies and integration points: Depends on arena allocation, histogram logging, column family options, prefix extractors, and RocksDB options. It is tightly coupled to `PlainTableBuilder` and `PlainTableReader`.

Risks: Raw pointer interpretation requires the index block bytes to outlive the index object. The high bit of bucket values is a type flag, so valid file offsets cannot exceed `kMaxFileSize`. Prefix strings are copied for change detection, which assumes sorted input groups identical prefixes contiguously.

Test signals: Header-level integration through plain table reader/builder, subindex decoding bounds, arena lifetime, huge-page allocation path, and prefix transition/sparseness behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.h -->

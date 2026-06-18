<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_builder.h

Purpose: Declares `PlainTableBuilder`, RocksDB's `TableBuilder` implementation for writing plain table SST files.

Important APIs and types: Constructor takes immutable/mutable options, property collector factories, column family metadata, file writer, user key size, encoding type, index sparseness, Bloom/index options, DB IDs, and file number. Overrides include `Add`, `status`, `io_status`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, `GetTableProperties`, checksum accessors, and `SetSeqnoTimeTableProperties`. `SaveIndexInFile()` exposes index storage mode.

Control flow: Callers add sorted internal keys and values, then call `Finish()` or `Abandon()`. Private prefix helpers choose total-order empty prefix when no prefix extractor is configured, otherwise transform user keys through the configured prefix extractor.

State and persistence: Members include an arena for index/Bloom allocation, options references, collectors, `BloomBlockBuilder`, optional `PlainTableIndexBuilder`, output file, offset, Bloom and huge-page configuration, status fields, table properties, `PlainTableKeyEncoder`, store-index flag, collected hashes, closed flag, and prefix extractor pointer.

Dependencies and integration points: Depends on plain table Bloom/index/key coding helpers, table properties, table builder interface, RocksDB options, and prefix extraction. The factory constructs this builder from `PlainTableOptions`.

Risks: The header exposes that the builder is not copyable and requires an explicit close path. It assumes inputs are sorted by comparator and internal keys contain the 8-byte trailer. Prefix behavior changes when no prefix extractor is configured, forcing plain encoding and total-order indexing.

Test signals: Builder lifecycle tests for finish/abandon/destruction, table property visibility before/after finish, prefix helper behavior with and without extractor, and construction from all plain table option combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.h -->

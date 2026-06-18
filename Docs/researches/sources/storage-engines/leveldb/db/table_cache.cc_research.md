# sources/storage-engines/leveldb/db/table_cache.cc

Purpose: implements `TableCache`, LevelDB's cache of opened SSTable `Table` objects and backing `RandomAccessFile`s. It reduces file open and table metadata parsing costs during reads, iteration, compaction, repair, and offset estimation.

Important APIs and functions: `TableAndFile`, `DeleteEntry`, `UnrefEntry`, `TableCache::FindTable`, `NewIterator`, `Get`, and `Evict`.

Control flow: `FindTable` encodes the file number as a fixed64 cache key, looks up an existing table, otherwise opens `<number>.ldb` or fallback `.sst`, calls `Table::Open`, and inserts the table/file pair into an LRU cache. `NewIterator` opens/looks up the table, returns a table iterator, and registers cleanup to release the cache handle when the iterator is destroyed. `Get` performs a direct `Table::InternalGet` and releases the handle immediately.

State and persistence behavior: cache state is memory-only. Entries own open file handles and parsed table metadata; `DeleteEntry` deletes both. Errors are deliberately not cached so a later repair or transient recovery can succeed.

Dependencies and integration: uses `NewLRUCache`, file naming helpers, `Env::NewRandomAccessFile`, `Table::Open`, `Iterator::RegisterCleanup`, and fixed64 coding. It is used by `Version::Get`, iterators over versions, compactions, repair scanning, and approximate offset calculations.

Risks and edge cases: `file_size` must match the actual table size expected by `Table::Open`. Cache keying by file number assumes LevelDB never reuses a number for a different live table without evicting. The fallback `.sst` path supports older filenames but can mask stale alternate files if metadata is wrong.

Test signals: covered indirectly by DB read/compaction tests, repair, and memenv DB tests. No dedicated table-cache unit test appears in this subset.

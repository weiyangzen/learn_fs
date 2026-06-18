# sources/storage-engines/leveldb/db/table_cache.h

Purpose: declares `TableCache`, a thread-safe facade for locating, opening, caching, iterating, and evicting table files by file number and size.

Important APIs and types: constructor `TableCache(dbname, options, entries)`, destructor, `NewIterator`, `Get`, `Evict`, and private `FindTable`.

Control flow: public methods resolve a file number to a cached `Table`; iterators retain cache handles through registered cleanup while direct gets release immediately after probing.

State and persistence behavior: contains `env_`, `dbname_`, a reference to immutable DB `Options`, and an owned `Cache*`. The cache persists only while the DB process is open.

Dependencies and integration: exposes the table lookup layer used by `VersionSet`, `Version`, repair, and compaction code. It depends on `Cache`, `Table`, `ReadOptions`, `Slice`, and internal key format definitions.

Risks and edge cases: because `options_` is stored by reference, the original `Options` object must outlive the cache through DB lifetime. Cache entry count controls open-file pressure.

Test signals: API contract is exercised through higher-level DB reads and version-set iterators.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.h -->
# sources/storage-engines/rocksdb/table/mock_table.h

Purpose: Declares the mock table format used by RocksDB tests to avoid real SST encoding while still exercising `TableFactory`, `TableBuilder`, and `TableReader` integration.

Important APIs and types: Defines `mock::KVPair`, `KVVector`, `MakeMockFile()`, `SortKVVector()`, `MockTableFileSystem`, `MockTableFactory`, and `MockTableReader`. `MockTableFactory` exposes corruption modes `kCorruptNone`, `kCorruptKey`, `kCorruptValue`, and `kCorruptReorderKey`, plus `CreateMockTable()`, `SetCorruptionMode()`, `SetKeyValueSize()`, assertion helpers, and table factory overrides. `MockTableReader` overrides iterator, get, approximate offset/size, memory usage, compaction setup, and table properties APIs.

Control flow: Tests configure a factory, build or directly create mock tables, then RocksDB opens readers through normal table factory hooks. The header makes clear that `CreateMockTable()` accepts internal-key/value pairs and bypasses the builder path.

State and persistence: `MockTableFileSystem` contains the in-memory map from file ID to sorted vectors. `MockTableFactory` owns the map, ID counter, corruption mode, and fake key/value size. `MockTableReader` references a stored vector and returns synthetic `TableProperties`.

Dependencies and integration points: Depends on RocksDB comparator/table abstractions, internal iterators, writable/random file wrappers via the implementation, `VersionEdit` types, port mutexes, and test harness utilities. It is not production table code.

Risks: `Clone()` returns `nullptr`, so code requiring cloneable table factories cannot use it. Reader lifetime depends on the factory map retaining referenced vectors. The format does not model compression, checksums, filters, range deletions, or real table properties.

Test signals: Compile tests using mock factory configuration, direct mock table creation, corruption modes, table reader get/iterator behavior, and assertion helpers for exactly one or latest generated files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.h -->

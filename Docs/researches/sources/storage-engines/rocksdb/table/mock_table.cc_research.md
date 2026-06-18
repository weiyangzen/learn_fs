<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.cc -->
# sources/storage-engines/rocksdb/table/mock_table.cc

Purpose: Implements an in-memory/mock RocksDB table factory, builder, reader, and iterator for tests. It simulates SST creation and reading by writing only a small file ID to disk and storing key/value vectors in a process-local map.

Important APIs and functions: Implements `MakeMockFile`, `SortKVVector`, `MockTableIterator`, `MockTableBuilder`, `MockTableReader::NewIterator`, `MockTableReader::Get`, `MockTableFactory::NewTableReader`, `NewTableBuilder`, `CreateMockTable`, `GetAndWriteNextID`, `GetIDFromFile`, `AssertSingleFile`, and `AssertLatestFiles`.

Control flow: Builders receive internal key/value pairs, optionally corrupt or reorder the first entries according to factory corruption mode, and on `Finish()` insert the vector into `MockTableFileSystem::files` under a generated ID. `NewTableBuilder()` writes the ID to the `WritableFileWriter`; `NewTableReader()` reads the ID back and returns a `MockTableReader` over the stored vector. Iterators perform lower/upper-bound seeks with `InternalKeyComparator`. `Get()` scans from the lookup key, parses internal keys, and feeds values into `GetContext::SaveValue()` until the context says to stop.

State and persistence: Persistent on-disk content is only the fixed 4-byte table ID. Actual table contents live in `MockTableFileSystem::files` protected by a mutex. `next_id_`, `corrupt_mode_`, and `key_value_size_` configure test behavior. Reader table properties are synthetic.

Dependencies and integration points: Integrates with the RocksDB `TableFactory`, `TableBuilder`, `TableReader`, `InternalIterator`, `GetContext`, file reader/writer wrappers, internal key parsing, and test assertion utilities.

Risks: The mock format is process-local; files are unreadable without the same factory instance state. `SeekToLast()` decrements `end()` without guarding empty tables. Corruption mode is intentionally one-shot and can produce invalid ordering or parse failures. `GetIDFromFile()` asserts a 4-byte read before checking error paths.

Test signals: Useful for DB/table tests that need deterministic table contents, builder corruption injection, latest-file assertions after compaction, get-path `SaveValue()` behavior, iterator seek/prev/next semantics, and file-not-found behavior for unknown IDs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/mock_table.cc -->

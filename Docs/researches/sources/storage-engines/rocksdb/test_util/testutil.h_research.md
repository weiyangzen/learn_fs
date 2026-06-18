# sources/storage-engines/rocksdb/test_util/testutil.h

Purpose: declares and defines a large set of inline test doubles and helpers for RocksDB unit tests, spanning in-memory file abstractions, comparators, background-task synchronization, compaction/merge test objects, custom compression wrappers, random option factories, filesystem probes, and object registration.

Important APIs/types: `RandomKeyType`, `UserDefinedTimestampTestMode`, `PlainInternalKeyComparator`, `SimpleSuffixReverseComparator`, `StringSink`, `RandomRWStringSink`, `OverwritingStringSink`, `StringSource`, `SeqStringSource`, `StringFS`, `NullLogger`, `SleepingBackgroundTask`, `FilterNumber`, `CompressorCustomAlg`, and `DecompressorCustomAlg` are the major reusable test types. Function declarations cover randomization, key building, file corruption/truncation, env creation, file type/number parsing, and registration.

Control flow and state: in-memory file types store contents in strings or maps and implement selected RocksDB file interfaces. `SleepingBackgroundTask` coordinates a background sleeper with mutex/condvar state. Custom compression prepends a five-byte header containing the custom type and dictionary hash, then delegates to LZ4; decompression strips/checks the header and delegates. `ReadOptionsNoIo` sets block-cache-only reads.

Dependencies/integration: includes Env, FileSystem, table, iterator, merge, compaction, compression, and mutex utilities. It is a central include for tests needing lightweight RocksDB-compatible objects.

Risks and test signals: many test doubles intentionally implement only part of their interface and return `NotSupported` elsewhere. `StringSource` can return direct slices in mmap mode or scratch-backed slices otherwise. Custom decompression has an `allowed_types_` field that must be enforced by users/tests. Tests should cover in-memory read/write semantics, compression header round trips, background wakeup paths, and no-I/O read options.

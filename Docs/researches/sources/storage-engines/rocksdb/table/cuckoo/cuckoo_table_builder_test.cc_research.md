# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_builder_test.cc

Purpose: unit tests for cuckoo table builder file layout, properties, collision handling, and failure modes.

Important APIs/types/functions: `hash_map` plus `GetSliceHash` give deterministic hash locations for tests. `CuckooBuilderTest` provides `CheckFileContents`, `GetInternalKey`, `NextPowOf2`, and `GetExpectedTableSize`. `CheckFileContents` reads the generated file, validates table properties, and checks every bucket against expected locations or empty-bucket filler bytes.

Control flow: tests create temporary writable files, instantiate `CuckooTableBuilder` with deterministic hash callback, add keys, assert incremental `NumEntries`/`FileSize`, finish and close, then inspect properties and raw buckets. Some tests use full internal keys; others use zero-sequence last-level mode where only user keys are stored.

State and persistence: tests write actual cuckoo table files under per-thread DB paths and read them back with `RandomAccessFileReader` and `ReadTableProperties`. Expected properties include empty key, value length, hash table size, hash function count, cuckoo block size, last-level flag, raw sizes, and data size.

Dependencies/integration: depends on file readers/writers, table properties reader, meta blocks, internal key builder/parser, bytewise comparator, and test harness.

Risks and test signals: coverage includes empty file, no-collision writes, collision writes, cuckoo block probing, displacement paths, user-key/last-level mode, too-long collision failure, duplicate key failure, value and deletion paths. It does not cover module-hash production hashing heavily, checksum names, factory integration, or crash cleanup of partially written files.

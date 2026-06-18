<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_sanity_test.cc -->
# sources/storage-engines/rocksdb/tools/db_sanity_test.cc

## Purpose
`db_sanity_test.cc` is a standalone create/verify utility that builds small RocksDB databases under multiple option configurations and later verifies that they can be reopened and read correctly. It is aimed at broad sanity coverage of table factories, comparators, filters, and compression variants.

## Important APIs, Types, and Functions
- `SanityTest` is the abstract base. It stores a root path, defines `Name()` and `GetOptions()`, and implements `Create()` and `Verify()`.
- `SanityTest::Create()` destroys any old named DB, opens with `create_if_missing`, writes one million `keyN -> valueN` records, and flushes.
- `SanityTest::Verify()` reopens with the same options and reads back all one million keys.
- Derived classes configure specific options: `SanityTestBasic`, `SanityTestSpecialComparator`, `SanityTestZlibCompression`, `SanityTestZlibCompressionVersion2`, `SanityTestLZ4Compression`, `SanityTestLZ4HCCompression`, `SanityTestZSTDCompression`, `SanityTestPlainTableFactory`, and `SanityTestBloomFilter`.
- `RunSanityTests(command, path)` allocates the test set, dispatches to `Create()` or `Verify()`, reports status, deletes each object, and returns aggregate success.

## Control Flow
`main()` expects `<path> [create|verify]`, normalizes the path to end in `/`, and calls `RunSanityTests()`. For `create`, each derived test destroys and recreates its own database directory named by `path + Name()`. For `verify`, each test opens its existing database and validates every key/value pair. The test list is suppressed under `__clang_analyzer__` to avoid false positives.

## State and Persistence Behavior
Each option profile maps to a separate physical RocksDB directory. The utility writes one million records and flushes them, leaving persisted SST and metadata for later verification. Comparator and table factory settings must be identical between create and verify, because RocksDB requires matching comparator/table behavior to read existing files.

## Dependencies and Integration Points
The file uses core RocksDB DB APIs, `Env`, comparators, compression enum values, block-based and plain table factories, prefix transforms, Bloom filters, and `Status`. It integrates as a command-line tool rather than a gtest. It references version macros for block-based table `format_version = 2` compatibility.

## Risks and Edge Cases
- Compression profiles require their corresponding compression libraries; missing libraries can make create fail.
- The special comparator is manually allocated and deleted; ownership is simple but not RAII.
- PlainTable requires a prefix extractor and mmap reads, so filesystem and platform behavior can affect it.
- Writing one million keys per profile is intentionally heavy for a sanity tool and may be slow or disk-intensive.
- Path concatenation depends on `main()` appending a slash.

## Test Signals
The program prints each profile name and `Status::ToString()` result. Exit code zero means all profiles succeeded; exit code one means at least one create or verify operation failed. A corruption status in `Verify()` pinpoints key/value mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_sanity_test.cc -->

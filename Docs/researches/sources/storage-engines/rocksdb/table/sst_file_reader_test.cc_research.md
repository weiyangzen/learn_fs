# sources/storage-engines/rocksdb/table/sst_file_reader_test.cc

Purpose: provides unit tests for `SstFileReader` and related `SstFileWriter` behavior, focusing on reading externally created SSTs, parsing raw table keys, timestamps, entry-count verification, and get/multiget edge cases.

Important APIs/types/functions: helper functions `EncodeAsString` and `EncodeAsUint64`; fixture `SstFileReaderTest` with `CreateFile`, `CheckFile`, and `CreateFileAndCheck`; timestamp fixtures using `BytewiseComparatorWithU64TsWrapper`; `SstFileReaderTableIteratorTest`; and parameterized `SstFileReaderTableGetTest` over single-get vs multiget.

Control flow: tests create SSTs with `SstFileWriter` or a temporary DB, open them with `SstFileReader`, then verify DB-style iteration, raw table iteration, checksum verification, parsing of internal keys, point lookups, merge resolution, and corruption handling. Timestamp tests write entries in comparator order and check snapshot-time visibility via `ReadOptions.timestamp`.

State and persistence behavior: tests create per-thread temporary SST/DB paths and clean them in destructors or via `DestroyDB`. Some tests intentionally ingest files into a DB to produce global sequence numbers or use sync points to corrupt table properties.

Dependencies/integration points: integrates test harness, DB test utilities, merge operators, custom comparators, external SST writer properties, convenience registration, blob/wide-column APIs, snapshots, live-file metadata, and sync points.

Risks covered: out-of-scope `ReadOptions` lifetime for `NewIterator`; timestamp size mismatch; timestamp ordering; non-persisted timestamp min-only rules and metadata stripping; corrupted `num_entries`; invalid short internal keys; blob-backed wide-column lookup without a fetcher; raw table iterator semantics differing from DB iterator semantics.

Test signals: this is the main test signal for the listed reader/writer APIs. It explicitly checks both `Get` and `MultiGet` via parameterization, and it distinguishes visible DB results from raw table entries including deletions and timestamps.

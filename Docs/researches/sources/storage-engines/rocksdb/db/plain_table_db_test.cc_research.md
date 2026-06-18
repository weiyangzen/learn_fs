# sources/storage-engines/rocksdb/db/plain_table_db_test.cc

## Purpose
`plain_table_db_test.cc` is a comprehensive test suite for RocksDB's PlainTable format. It validates non-mmap reads, option compatibility, flushing, bloom/index metadata, read-only/mmap pinning, iteration, long keys, custom comparators, hash bucket conflicts, compaction triggering, adaptive table opening, and unsupported range deletes.

## Important APIs, Types, And Functions
`PlainTableKeyDecoderTest.ReadNonMmap` tests `PlainTableFileReader` buffering over a `StringSource`.

`PlainTableDBTest` is parameterized by mmap mode. It builds default PlainTable options with prefix extractor, hash-link-list memtable, and disabled concurrent/unordered writes. Helpers provide reopen/destroy, `Put`, `Delete`, `Get`, level file counts, and iterator status.

`TestPlainTableReader` subclasses `PlainTableReader` to verify metadata, populate index, and assert Bloom matches/misses. `TestPlainTableFactory` subclasses `PlainTableFactory` to read table properties/meta blocks, verify on-file Bloom/index blocks when configured, and create the test reader.

## Control Flow
Option tests verify that PlainTables built with a prefix extractor cannot be reopened without one or with a different one, while tables built without a prefix extractor require `hash_table_ratio == 0`. Flush tests iterate over huge-page size, encoding type, Bloom/full-scan mode, total-order mode, and index-in-file mode, checking reads, table-reader memory, table properties, and full-scan iteration behavior.

`Flush2`, `BloomSchema`, and iterator tests use `TestPlainTableFactory` to verify Bloom behavior, table properties, column-family metadata, and seek behavior. `Immortal` compares value pin/copy behavior in normal and read-only reopen, with mmap mode avoiding copies after reopen.

Iterator tests cover fixed and variable key length, prefix and plain encoding, long keys, reverse suffix comparator ordering, and bucket-conflict behavior. Hash bucket tests force conflicts and validate both point lookups and seeks for existing and non-existing keys under normal and reverse suffix comparators.

`CompactionTrigger` configures small write buffers and an L0 trigger to ensure PlainTable output participates in normal compaction scheduling. `AdaptiveTable` writes PlainTable data, reopens with an adaptive factory, verifies existing and new data, then demonstrates that opening with only the wrong table factory fails to read expected values when paranoid checks are disabled. `DeleteRangeNotSupported` verifies range deletes fail directly and inside a write batch, preserve atomicity, poison subsequent flush/put until reopen, and do not corrupt recoverable WAL state.

## State And Persistence Behavior
The tests repeatedly create real PlainTable SSTs and reopen them with compatible or incompatible options. They inspect persisted table properties, optional persisted Bloom/index meta blocks, table-reader memory estimates, and level file counts.

Read-only and mmap behavior affects whether value reads are copied or pinned. Range-delete unsupported state demonstrates an error path where WAL recovery remains valid but the current memtable/flush path rejects unsupported range tombstones.

Compaction tests verify PlainTable files are normal LSM participants: flush creates L0 files and reaching the trigger compacts to L1.

## Dependencies And Integration Points
The file depends on DB internals, version set/write batch helpers, filename utilities, cache/table APIs, PlainTable reader/factory/key-coding/Bloom/index classes, meta-block readers, table builders, hash utilities, random/string utilities, merge operators, and GoogleTest parameterization.

Integration points include table factory option serialization, prefix extractors, Bloom filters, `ReadTableProperties`, meta-block lookup, column-family properties, DB open/read-only open, compaction, adaptive table factory dispatch, and write-batch atomicity.

## Risks
PlainTable option compatibility is strict. Reopening with missing/different prefix extractors or hash mode without prefixes can fail or produce unreadable tables. Tests cover both expected hard failures and adaptive-factory success.

Bloom schema tests rely on known false-positive bit patterns and cache-line size; legitimate Bloom implementation changes can require updating expected patterns. Many iterator tests depend on comparator-specific ordering and prefix extractor behavior, so comparator/prefix mismatches are high risk.

Unsupported range deletes are dangerous because a WriteBatch must remain atomic and existing keys must survive even though the operation leaves the DB unable to flush until reopen.

## Test Signals
Success signals include exact error strings for bad options, correct table property values, Bloom miss callbacks for absent keys, correct iteration order under normal and reverse comparators, successful long-key scans, expected file movement from L0 to L1, adaptive factory reads across reopen, `NotSupported` for range deletes and subsequent writes/flushes, and recovery preserving pre-error keys.

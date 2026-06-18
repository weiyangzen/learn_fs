# sources/storage-engines/rocksdb/utilities/trie_index/trie_index_db_test.cc

## Purpose

DB-level integration coverage for the experimental trie-based User Defined Index (UDI). The suite verifies that RocksDB block-based tables written with `TrieIndexFactory` remain readable and iterable through flush, compaction, reopen, external SST ingest, transactions, snapshots, range tombstones, prefix iteration, coalescing iterators, and primary-vs-secondary UDI modes. It complements lower-level SST tests by exercising the full DB path: memtables, WAL replay, `CompactionIterator`, block-based table building, table reader routing, and `ReadOptions::table_index_factory`.

## Important APIs, types, and helpers

The test fixture `TrieIndexDBTest : testing::TestWithParam<bool>` runs every test twice: `false` means UDI is a secondary index selected by `ReadOptions::table_index_factory`; `true` means `BlockBasedTableOptions::use_udi_as_primary_index` routes default reads through the trie. `OpenDBImpl` installs a shared `TrieIndexFactory` in `BlockBasedTableOptions`, optionally forces small data blocks, and stores `last_options_` for cleanup. `OpenDBWithoutUDI`, `OpenDBPrimary`, and `OpenDBSecondary` model migration and rollback paths.

Reusable verification helpers compare standard-index and trie-index behavior for `Get`, `Get` at snapshot, `GetEntity`, `MultiGet`, forward scans, reverse scans, `Seek`, `SeekForPrev`, prefix scans, and lockstep multi-prefix scans. `StandardIndexReadOptions()` returns bare `ReadOptions`; `TrieIndexReadOptions()` sets `table_index_factory` only in secondary mode. Key helpers build fixed-width and stress-like bytewise keys, padded values, and an `SstQueryFilterConfigsManager::Factory` with `StressLikeVariableWidthExtractor` for range-query table filters.

## Control flow and behavior covered

The first test group writes all RocksDB operation types that matter to table building: `Put`, `Delete`, `Merge`, `SingleDelete`, `PutEntity`, `TimedPut` through `WriteBatch::TimedPut`, and `DeleteRange`. Tests flush or compact those records, then assert the same visible key/value view through both indexes. Snapshot-heavy compaction tests deliberately preserve multiple versions so the trie index must select the correct data block for a target sequence number.

The same-user-key tests force many versions of one or more keys across data block boundaries by using tiny block sizes and held snapshots. They verify the trie factory's seqno side-table and overflow-block logic through `Get`, `Seek`, forward scans, reverse scans, `Prev`, and compaction. `NonBoundarySeparatorSeekCorrectness` reproduces a bug class where `FindShortestSeparator` returns an unchanged separator for different user keys while seqno encoding is active; the expected behavior is that the trie does not incorrectly advance past the target block.

Iterator coverage includes `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, direction switching, `SeekForPrev`, upper and lower bounds, snapshot plus bound interactions, iterator stability across flushes, `auto_refresh_iterator_with_snapshot`, `allow_unprepared_value`, and `NewCoalescingIterator` for both single-CF and multi-CF scans. Prefix coverage uses fixed prefix extractors, `total_order_seek`, `auto_prefix_mode`, empty prefixes, bounds, deletes, merges, memtable-plus-SST mixes, compaction, and crash-test-like batches.

Persistence and deployment-path tests cover WAL replay, reopen with cold SST reads, external file ingest using `SstFileWriter`, many small L0 SSTs, overlapping L0 SSTs, mixed SSTs with and without UDI, reopening a UDI DB without a UDI factory, primary UDI migration, rejection of pre-UDI SSTs when primary UDI is required, rollback from primary to secondary, rollback from primary without compaction, and table property `udi_is_primary_index`.

## State and persistence behavior

The file uses a per-thread temporary DB path and destroys it in setup/teardown. Most tests force data into SSTs with `FlushOptions` so the trie UDI block is actually built and read. Compaction tests rewrite SSTs and check that the new output still carries a usable trie index. Snapshot tests pin old versions so internal keys for the same user key remain live in the table and exercise trie overflow selection. Reopen and WAL replay tests ensure that persisted MANIFEST, WAL, standard index blocks, UDI meta blocks, and table properties survive process-style boundaries.

Primary mode is treated as configuration-driven routing, not a separate file format that drops the standard index. Tests assert that standard index fallback still works when removing UDI after primary-mode SST creation, while opening primary mode over pre-UDI SSTs fails with corruption because the requested primary index block is absent. Migration tests require bottommost force compaction to rewrite legacy SSTs before enabling primary UDI.

## Dependencies and integration points

The suite depends on RocksDB DB APIs (`DB`, `TransactionDB`, `WriteBatch`, `SstFileWriter`, `IngestExternalFileOptions`, `CompactRangeOptions`, snapshots, iterators, wide columns), block table configuration (`BlockBasedTableOptions`, table properties, compression), merge operators, prefix transforms, table filters, and test utilities. It directly integrates with `utilities/trie_index/trie_index_factory.h` and indirectly with the UDI builder/reader wrapper in block-based table construction.

## Risks and edge cases

Primary risks are index/data iterator desynchronization, incorrect block choice when the same user key spans blocks, wrong handling of last-block separators, over-aggressive bound rejection, fallback failures for mixed UDI/non-UDI files, non-bytewise or binary key ordering bugs, stale snapshot reads after refresh, and missing support in non-Get paths such as `MultiGet`, `GetEntity`, checksums, transactions, and coalescing iterators. The tests also call out issues around `kTypeValuePreferredSeqno`, range tombstones across levels, external SSTs, compressed data blocks, and empty/deletion-only tables.

## Test signals

Passing signals are exact equality between standard-index and trie-index scans, point reads, snapshot reads, iterator movement, and status codes. The strongest signals are the parameterized primary/secondary run, full migration/rollback tests, same-user-key overflow tests, randomized multi-level `DeleteRange` consistency checks, stress-like prefix scans, and table property assertions. Some tests are intentionally skipped or bypassed when a mode is not applicable, such as secondary-only fallback tests or zlib-dependent compression coverage.

# sources/storage-engines/rocksdb/utilities/option_change_migration/option_change_migration_test.cc

## Purpose
This test file validates `OptionChangeMigration()` across compaction style and level-count transitions, data preservation, reopen safety, FIFO cases, and multi-column-family migrations.

## Important APIs, types, and functions
`DBOptionChangeMigrationTests` is parameterized by old/new level counts, compaction styles, dynamic-level flags, and FIFO max table file size. Test cases `Migrate1` through `Migrate4` run transitions in both directions and with different data generation patterns, preserving key sets for verification.

`DBOptionChangeMigrationTest.CompactedSrcToUniversal` covers a compacted level source migrating to universal with one level.

`DBOptionChangeMigrationMultiCFTest` covers `BasicMultiCF`, `DifferentStylesPerCF`, `ValidationMismatched`, and `FromFIFOMultiCF`.

## Control flow
Single-CF tests configure old options, write at least megabytes of data, wait for flush/compaction, snapshot all keys via iterator, close, call `OptionChangeMigration()`, reopen with new options, wait/reopen again, and assert exact key ordering/presence.

Multi-CF tests create an extra CF, write data to default and `cf1`, collect key sets, close, build old/new descriptor vectors, migrate, reopen all CFs, and verify data per CF. Validation tests call migration with missing, renamed, or reordered CF descriptors and expect `InvalidArgument`.

## State and persistence behavior
Tests use real DB directories through `DBTestBase` with fsync enabled. They intentionally exercise persistent compaction output and manifest rewriting across close/reopen cycles. CF handles are manually deleted/destroyed.

## Dependencies and integration points
The file depends on `rocksdb/utilities/option_change_migration.h`, `db/db_test_util.h`, stack trace support, `Random`, and DB compaction/flush/test wait hooks.

## Risks and edge cases
The parameter comments sometimes label new values as old in tuple literals, but the tuple positions are clear in code. Tests focus on key preservation, not exact level layout after migration. Multi-CF cleanup skips destroying the default handle, matching DB ownership expectations.

## Test signals
Coverage is strong for successful migration and descriptor validation. It gives high confidence in data preservation across supported compaction-style transitions.

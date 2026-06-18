# sources/storage-engines/rocksdb/db/db_compaction_filter_test.cc

## Purpose
`db_compaction_filter_test.cc` verifies RocksDB compaction filter behavior across compaction, flush, recovery, snapshots, merge operands, range-skip decisions, column-family context, and unsupported filter configurations. It exercises both direct `CompactionFilter` instances and `CompactionFilterFactory` implementations, including the newer `FilterV2` decision API.

The suite establishes the expected contract for filtering table-file creation reasons: compaction filters may keep, delete, change, purge, or skip keys during eligible table creation, but their use is constrained by snapshots, merge semantics, manual/automatic compaction context, and `IgnoreSnapshots()` support.

## Important APIs, Types, And Functions
Global counters `cfilter_count` and `cfilter_skips` track filter invocation and skip behavior. `NEW_VALUE` is the replacement value used by `ChangeFilter`.

`DBTestCompactionFilter` is the base fixture. `DBTestCompactionFilterWithCompactParam` parameterizes selected tests over option configs: default, universal compaction, universal multi-level, level subcompactions, and universal subcompactions, with a reduced set under non-full Valgrind.

The file defines several filter implementations. `KeepFilter` counts and preserves keys. `DeleteFilter` removes values and merge operands. `DeleteISFilter` removes keys in a numeric range and returns `IgnoreSnapshots()=true`. `SkipEvenFilter` implements `FilterV2()` and returns `kRemoveAndSkipUntil` for zero-padded key ranges whose tens bucket is even. `ConditionalFilter` removes values equal to a configured byte string. `ChangeFilter` replaces values with `NEW_VALUE`.

Factory types include `KeepFilterFactory`, `DeleteFilterFactory`, `DeleteISFilterFactory`, `SkipEvenFilterFactory`, `ConditionalFilterFactory`, `ChangeFilterFactory`, and `TestNotSupportedFilterFactory`. `KeepFilterFactory` can assert fields in `CompactionFilter::Context`, including full/manual flags, column-family ID, input start level, and input table properties. `DeleteFilterFactory` is parameterized by `TableFileCreationReason` and opts in through `ShouldFilterTableFileCreation()`.

## Control Flow
The main `CompactionFilter` test first writes 100,000 keys to a non-default column family, manually compacts from L0 to L1 and L1 to L2 with a keep filter, and asserts every key passes through the filter at each level. It then inspects internal keys at the bottom level to confirm sequence numbers are zeroed where allowed. After overwriting the same keys, it repeats the compaction path and invocation counts. The second half reopens with a delete filter for compaction-created files, compacts, and verifies the database is empty.

`CompactionFilterDeletesAll` covers the edge case where compaction output contains no keys. It writes several flushed files, compacts with a delete filter, expects zero live files, reopens, and scans an empty DB, ensuring the version edit can contain deletes without adds.

`CompactionFilterFlush` and `CompactionFilterRecovery` configure the same delete factory for `kFlush` or `kRecovery`. They prove filtering is applied only to the selected table-file creation reason: flush filtering deletes puts/merges during flush but not recovery or compaction, while recovery filtering deletes WAL-recovered records but not flushed or compacted records.

`CompactionFilterWithValueChange` runs under the parameterized option configs. It writes 100,001 keys, compacts them down, rewrites them, compacts again with `ChangeFilterFactory`, and verifies every key reads as `NEW_VALUE`. The extra key and compaction style branches exercise snapshot/sequence constraints and universal compaction paths.

`CompactionFilterWithMergeOperator` uses the uint64-add merge operator and `ConditionalFilterFactory` to validate merge interactions. It confirms filter removal of a base value is ignored when merge operands for the same key must be preserved in the same compaction, a lone value can be deleted before later merges, filters do not apply to merge keys, and combined value/merge histories still resolve correctly.

Context tests verify factory inputs. `CompactionFilterContextManual` uses universal compaction, manual full compaction, input table property capture, and internal iteration to assert 700 keys and zeroed sequences after compaction. `CompactionFilterContextCfId` checks the non-default column family ID in automatic compaction context.

Snapshot and skip tests exercise advanced decisions. `CompactionFilterIgnoreSnapshot` keeps a snapshot after the first flush, deletes selected numeric keys despite snapshots because the filter ignores snapshots, validates snapshot and latest iterator counts, then releases the snapshot. `SkipUntil` and `SkipUntilWithBloomFilter` use `FilterV2::kRemoveAndSkipUntil` to delete even tens buckets and skip scanning to the next boundary, including a prefix Bloom configuration.

Unsupported behavior is explicit. `IgnoreSnapshotsFalse`, `IgnoreSnapshotsFalseDuringFlush`, and `IgnoreSnapshotsFalseRecovery` configure filters whose `IgnoreSnapshots()` returns false and expect compaction, flush, or recovery to return `NotSupported`. `DropKeyWithSingleDelete` verifies a `FilterV2` that purges key `b` and removes other keys can coexist with later `SingleDelete` and bottommost compaction without corrupting single-delete semantics.

## State And Persistence Behavior
The suite repeatedly writes, flushes, compacts, reopens, and scans to distinguish transient read behavior from persisted table state. Delete filters should remove keys from output SSTs and manifest state, including the all-deleted case where no new table files are added. Keep filters should preserve keys while allowing bottom-level sequence number zeroing. Change filters must persist rewritten values into compacted output files.

Creation reason filtering changes when data becomes persistent. A filter for `kFlush` affects memtable-to-SST output but not WAL recovery; a filter for `kRecovery` affects recovered WAL contents but not normal flush; a filter for `kCompaction` applies to manual compaction-created files in these tests while automatic compaction may be deliberately skipped by `DeleteFilterFactory`.

Snapshot handling is a persistence contract. Ordinary compaction filtering cannot ignore snapshots unless `IgnoreSnapshots()` is true; unsupported filters must fail rather than dropping data still visible to snapshots. `DeleteISFilter` shows the opposite contract: a filter that explicitly ignores snapshots can remove records regardless of snapshot visibility, changing what snapshot iterators see according to the tested count expectations.

Merge persistence is constrained by merge semantics. Compaction filters are not allowed to blindly delete merge operands or base values when that would alter the resolved merged value for visible history. The merge test encodes those cases with fixed64 values and an additive merge operator.

## Dependencies And Integration Points
This file depends on `db/db_test_util.h` for DB fixtures, compaction helpers, internal iterators, column-family helpers, key/value operations, and utility assertions. It also uses `port/stack_trace.h`, GoogleTest parameterization, RocksDB `CompactionFilter` and `CompactionFilterFactory` APIs, `CompactionFilter::Context`, `TableFileCreationReason`, merge operators, table factories, Bloom filter policy, prefix extractors, snapshots, internal key parsing, and `CompactRangeOptions`.

Integration points include manual/internal compaction helpers (`TEST_CompactRange`, `CompactRange`), sequence-number zeroing at bottom levels, column family handles and IDs, universal and level compaction styles, subcompactions, block-based table prefix Bloom filters, WAL recovery, flush, merge resolution, single-delete correctness, and table property collection passed into filter context.

## Risks
The global counters are intentionally simple but require each test to reset them before assertions. Parallel test execution within the same process would be unsafe unless RocksDB test runners isolate these tests appropriately.

Several tests depend on exact filter invocation counts, sequence-number zeroing, level placement, and manual compaction behavior. Changes to compaction picking, universal compaction layout, or bottommost sequence optimization can break assertions even when user-visible data remains correct, so failures should be interpreted against the intended internal contract.

Snapshot and merge interactions are correctness-sensitive. Allowing a filter with `IgnoreSnapshots()=false` to proceed during compaction/flush/recovery could silently drop visible data. Applying filters to merge operands incorrectly could change merge results. `DropKeyWithSingleDelete` covers a narrow single-delete hazard where purging/removing keys must not leave an invalid tombstone/value pairing.

`SkipEvenFilter` assumes zero-padded numeric keys and constructs `skip_until` boundaries with `snprintf`. It is a targeted test for `FilterV2` skip semantics, not a general parser-safe filter pattern for arbitrary user keys.

## Test Signals
Useful success signals include exact `cfilter_count` values for manual level compactions, `cfilter_skips` values for skip-until tests, expected live-file counts after all-delete compaction, empty scans after deletion filters, persisted `NEW_VALUE` reads after value-changing compaction, correct context fields in factory creation, expected snapshot/latest iterator counts after snapshot-ignoring deletes, `NotSupported` statuses for unsupported filters, and successful reopen/compaction after single-delete purge scenarios.

Regression failures identify specific contracts: creation-reason routing, merge operand preservation, sequence-number zeroing, column-family context propagation, skip-until range pruning, snapshot safety checks, and cleanup/manifest handling when a compaction filter produces no output.

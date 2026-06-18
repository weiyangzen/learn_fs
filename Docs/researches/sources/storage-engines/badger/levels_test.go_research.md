<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/levels_test.go -->
# sources/storage-engines/badger/levels_test.go

## Purpose
This test file validates Badger LSM compaction, lookup, version-retention, range-split, and stale-data cleanup behavior. It constructs synthetic SSTables directly, installs them into levels, and runs `levelsController` operations without relying solely on background compaction.

## Important APIs, Types, And Functions
`createAndOpen` builds a table from `keyValVersion` rows, writes a manifest create change, and appends the table to a target level. `getAllAndCheck` iterates all internal versions and checks key/value/version/meta ordering. Test cases include `TestCheckOverlap`, `TestCompaction`, `TestCompactionTwoVersions`, `TestCompactionAllVersions`, `TestDiscardTs`, `TestDiscardFirstVersion`, skipped `TestL1Stall`/`TestL0Stall`, `TestLevelGet`, `TestKeyVersions`, `TestSameLevel`, `TestTableContainsPrefix`, `TestFillTableCleanup`, `TestStaleDataCleanup`, and `TestBaseLevelZeroBySize`.

## Control Flow
Most tests disable background compactors and enable managed timestamps, create deterministic table layouts, set discard timestamps, call `runCompactDef` or `doCompact`, then verify the complete visible internal key stream. The tests cover L0-to-Lbase, level-to-next-level, same-level Lmax compaction, tombstone handling with and without lower-level overlap, split compactions, and explicit `compactStatus` add/delete behavior.

## State And Persistence Behavior
The tests mutate actual table files and manifest records under temporary DB directories, so they exercise on-disk SSTable creation and manifest bookkeeping. They verify that compaction rewrites table state without losing expected live versions, and that stale-data size on a level drops after Lmax cleanup. `TestKeyVersions` compares disk and in-memory range split counts.

## Dependencies And Integration Points
The suite uses `runBadgerTest`, `DefaultOptions`, `Open`, `table.NewTableBuilder`, `table.CreateTable`, `pb.ManifestChange`, `newCreateChange`, `levelHandler`, and internal key helpers from `y`. It validates `levels.go` together with table building, manifest persistence, iterator ordering, and managed transaction timestamp semantics.

## Risks And Edge Cases
Skipped stall tests mean L0/L1 blocking behavior is documented but not currently enforced. Some tests build tables manually and may bypass normal write-path invariants. The compaction expectations are sensitive to internal iterator ordering and version encoding, so legitimate storage layout changes require careful test updates. The base-level-zero regression test protects a large-database edge where dynamic level sizing previously left `baseLevel == 0`.

## Test Signals
Strong signals are exact internal key streams before and after compaction, absence of panic for huge Lmax sizes, zero stale data after cleanup, prefix membership truth tables, and blocked compaction status reuse after `cstatus.delete`. Failures indicate regression in snapshot safety, tombstone pruning, dynamic base-level calculation, range overlap, or same-level compaction cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/levels_test.go -->

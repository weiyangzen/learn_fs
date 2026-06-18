# sources/storage-engines/badger/db2_test.go

## Purpose
`db2_test.go` is a high-risk regression and stress test suite for Badger database behavior that is not fully covered by the smaller API tests. It focuses on value-log truncation and replay, large key/value limits, compaction table selection, value-log GC interactions, Windows mmap recovery, drop operations, version accounting, stream-writer key counts, and startup/read-only guarantees.

## Important APIs, Types, and Functions
- `TestTruncateVlogWithClose`, `TestTruncateVlogNoClose*`: exercise value-log truncation after clean close and manual crash-style reopen scenarios.
- `TestBigKeyValuePairs`, `TestPushValueLogLimit`, `TestBigValues`: validate boundary handling around key sizes, value sizes, and value-log file limits; most are manual due to resource cost.
- `BenchmarkDBOpen`: measures read-only open cost against a prebuilt Badger directory.
- `TestCompactionFilePicking`, `addToManifest`, `createTableWithRange`: build synthetic SST tables and manifest entries to verify compaction ordering heuristics.
- `TestReadSameVlog`: repeatedly reads values from the same value log in plain and encrypted configurations.
- `TestL0GCBug`: disabled regression scenario for `KeepL0InMemory` with value-log GC.
- `TestWindowsDataLoss`: Windows-only recovery regression for value-log mmap expansion and simulated crash.
- `TestDropPrefixWithNoData`, `TestDropAllDropPrefix`: validate prefix/drop concurrency and no-op prefix drops.
- `TestIsClosed`, `TestMaxVersion`, `TestTxnReadTs`, `TestKeyCount`, `TestAssertValueLogIsNotWrittenToOnStartup`: cover lifecycle, timestamp, stream writer, and read-only startup invariants.

## Control Flow and State
Most tests create temporary Badger directories, open a DB with targeted options, perform transactional writes, close or intentionally simulate a crash, reopen, and then verify reads or internal counters. Crash simulations release directory guards and avoid normal close paths to expose replay behavior. Compaction tests write table files directly through `table.CreateTable`, register manifest changes, insert tables into selected levels, and then call compaction heuristics. Drop tests coordinate goroutines retrying on `ErrBlockedWrites` to verify serialization around destructive operations.

## Persistence Behavior
The file heavily exercises durable state: value-log files (`*.vlog`), SST manifests, table metadata, timestamps, and read-only reopen behavior. `TestTruncateVlogWithClose` physically truncates `000001.vlog`; `TestWindowsDataLoss` manipulates mmap/file handles and expects all original keys after reopen; `TestAssertValueLogIsNotWrittenToOnStartup` asserts read-only open and reads do not mutate latest vlog size.

## Dependencies and Integration Points
Tests integrate with `Open`, `OpenManaged`, `DB.Update`, `DB.View`, `RunValueLogGC`, `DropPrefix`, `DropAll`, `MaxVersion`, stream writer APIs, the levels controller, manifest changes, table builders, and `ristretto/z` mmap helpers. They use `testify/require`, `pb.ManifestChange`, `table.Table`, Badger options, and low-level `y` key helpers.

## Risks and Edge Cases
The riskiest paths are crash recovery after partial value-log records, massive values near `math.MaxInt32`, large manual tests that are skipped by default, Windows-only mmap behavior, and direct manipulation of level internals. Several tests are manual or disabled, so they document expected behavior but do not protect normal CI unless explicitly enabled.

## Test Signals
This is itself a test file. It provides strong regression signals for storage durability, GC, compaction picking, version handling, and read-only startup. Manual skips should be treated as reduced automated coverage for extreme value-size and long-running stream-writer scenarios.

# sources/storage-engines/pebble/range_del_test.go

## Purpose

`range_del_test.go` tests and benchmarks Pebble range deletion behavior. It covers datadriven range tombstone semantics, delayed flushing for range deletions and range keys, stress around concurrent delayed flush triggers, correctness of range tombstone truncation during compactions across levels, and iterator performance when many keys are covered by tombstones.

## Important APIs, Types, and Functions

- `TestRangeDel` runs `testdata/range_del` with commands for defining DB contents, waiting for table stats, compacting, getting keys, and iterating at optional sequence numbers.
- `TestFlushDelay` verifies that all supported ways to write range deletions or range keys trigger the configured flush delay: direct DB calls, batch commits, deferred batch operations, `SetRepr`, and `Apply`.
- `TestFlushDelayStress` runs concurrent random `DeleteRange`, `RangeKeySet`, and `Set` operations with small memtables and flush delays under `synctest`.
- `TestRangeDelCompactionTruncation`, `TestRangeDelCompactionTruncation2`, and `TestRangeDelCompactionTruncation3` construct small target-file-size LSMs to verify range tombstones are truncated to compaction/table boundaries and do not incorrectly delete newer keys in lower levels.
- `BenchmarkRangeDelIterate` and `benchmarkRangeDelIterate` measure iterator behavior when an ingested sstable is mostly or fully covered by a range tombstone, with and without a snapshot plus compaction scenario.

## Control Flow and State

`TestRangeDel` manages a single DB across datadriven commands. `define` closes any prior DB, opens a new one with automatic compactions disabled, forces base level 1 for deterministic output, and returns memtable/version state. `compact` runs a command helper, again forces base level 1, and returns the current version string. `get` and `iter` query visible state, with `iter` able to use a custom sequence number by constructing a `Snapshot` with `base.SeqNum`.

`TestFlushDelay` opens a memfs DB with both `FlushDelayDeleteRange` and `FlushDelayRangeKey` set. Before each write case, it captures the current mutable memtable's `flushed` channel under `d.mu`; after the write commits, it waits on that channel, proving the delayed flush fired. The cases deliberately cover alternate write paths so range operations cannot bypass the flush-delay accounting.

`TestFlushDelayStress` repeats randomized concurrent writes across multiple DB instances. It uses `runtime.GOMAXPROCS(0)` writers, randomized keys, tiny memtables, and short sleeps before waiting for all writers. This is mainly a race/deadlock/regression signal around scheduling delayed flushes while memtables rotate.

The compaction truncation tests force specific LSM shapes by using small `TargetFileSizes`, snapshots that preserve old versions, manual compactions over narrow bounds, and direct version string assertions. They verify both positive visibility (`Get("b")` succeeds when a higher-level tombstone should not cover it) and negative visibility (`ErrNotFound` remains correct after further compactions).

The benchmark builds an external sstable with `sstable.NewRawWriter`, ingests it, writes a range tombstone covering most or all keys, optionally holds a snapshot and compacts, and repeatedly creates an iterator and seeks to the tombstone start.

## Persistence and State Behavior

The tests exercise persistent state through flushed sstables, ingested external sstables, WAL-backed writes, snapshots, range tombstones, and compaction outputs. Range tombstones are persisted in sstable range-deletion blocks and may have wider bounds on disk than an individual output table. The truncation tests specifically guard the invariant that in-memory/table metadata boundaries used during compaction prevent a tombstone in one table or level from deleting newer keys outside its effective file/compaction bounds.

Flush-delay tests verify memtable lifecycle state: once a range deletion or range key is added, Pebble should schedule a flush so disk space can be reclaimed and lazy combined iteration is not blocked indefinitely. The stress test probes this behavior under concurrent writes and memtable rotation.

## Dependencies and Integration Points

The file depends on `datadriven`, `synctest`, `leaktest`, `require`, `vfs`, `manifest`, `testkeys`, `testutils`, `objstorageprovider`, `sstable`, and Pebble helpers such as `runDBDefineCmd`, `runCompactCmd`, `runGetCmd`, `runIterCmd`, `runWaitForTableStatsCmd`, `closeAllSnapshots`, and `randStr`.

Production APIs under test include `DB.DeleteRange`, `Batch.DeleteRange`, `Batch.DeleteRangeDeferred`, `Batch.SetRepr`, `Batch.Apply`, `DB.RangeKeySet`, `DB.RangeKeyUnset`, `DB.RangeKeyDelete`, range-key batch operations, `DB.Flush`, `DB.Compact`, `DB.Get`, `DB.NewIter`, `DB.Ingest`, snapshots, and internal version/compaction state.

## Risks and Edge Cases

- The compaction truncation tests are tightly coupled to file sizing, estimated sizes, format versions, and resulting file numbers. Comments acknowledge that some scenarios need future datadriven rewrites for newer table formats.
- Range tombstone correctness is subtle because on-disk tombstone spans may exceed table boundaries. Bugs can cause deletion of newer keys in lower levels or incorrect LSM bounds expansion.
- Flush-delay behavior must avoid both missed flushes and excessive flush churn. Concurrent stress helps catch races but may still be timing-sensitive.
- Tests manipulate internal DB state such as `dynamicBaseLevel`, `forceBaseLevel1`, and version strings, so compaction picker or LSM formatting changes may require updates.
- Benchmarks ingest generated sstables and use snapshots to reproduce known expensive iteration patterns; changes to iterator tombstone skipping may shift results significantly.

## Test Signals

This file is direct test coverage for range deletion behavior. It provides datadriven semantic coverage, targeted regression tests for tombstone truncation during compaction, delayed-flush path coverage for range deletions and range keys, concurrency stress under synthetic time, and benchmark signals for iterator performance over tombstone-heavy data.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manual_compaction_test.cc -->
# sources/storage-engines/rocksdb/db/manual_compaction_test.cc

## Purpose
Tests manual compaction behavior, including an old regression where deleted data could reappear, compaction filter coverage across manual ranges, and skipping levels/ranges with no overlapping files.

## Important APIs, Types, And Functions
`ManualCompactionTest` creates a per-thread DB path and destroys stale state in its constructor. `DestroyAllCompactionFilter` drops entries whose value is `"destroy"`. `LogCompactionFilter` records which level each key was compacted at and exposes `Reset()`, `NumKeys()`, and `KeyLevel()`. Helpers `Key1()` and `Key2()` generate related key ranges, and `kNumKeys` controls reduced-size regression data.

## Control Flow
`CompactTouchesAllKeys` runs once for level compaction and once for universal compaction, writes four keys, compacts through `key4`, and verifies only `key3` survives after the compaction filter removes `"destroy"` values. `Test` writes one key range, writes a second suffixed range, deletes the second range, manually compacts only the first range, then iterates the DB and expects exactly the first range to remain. `SkipLevel` creates three flushed L0 files with keys `1`, `2`, and `[4,8]`, then issues several compact ranges and checks whether the compaction filter saw the expected keys/levels as files move from L0 to L1.

## State And Persistence Behavior
The tests create and destroy real RocksDB instances under a test path. They force no compression and small write buffers/flushes to shape the LSM. Manual compactions rewrite SST state and trigger compaction filters. The final assertions inspect persistent key visibility through iterators and filter-observed level state.

## Dependencies And Integration Points
Uses the public RocksDB `DB` API, `Options`, `CompactRangeOptions`, `FlushOptions`, `WriteBatch`, iterators, compaction filters, and the test harness. It validates DB compaction scheduling/selection behavior rather than the lower-level compaction implementation directly.

## Risks And Edge Cases
The tests rely on deterministic LSM shape from flushes, compression disabled, fixed level options, and manual compaction range boundaries. If compaction picker heuristics or level placement changes, `SkipLevel` expectations may need adjustment. `options.compaction_filter` is a raw pointer manually deleted after DB close, so test lifetime ordering matters.

## Test Signals
The file itself is a test signal. Failures indicate manual compaction skipped needed keys, compacted unnecessary levels, resurrected deleted keys, mishandled compaction filters, or changed level/range overlap semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/manual_compaction_test.cc -->

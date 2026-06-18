<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/metrics_test.go -->
# sources/storage-engines/badger/metrics_test.go

## Purpose
This file tests Badger's expvar metrics for user writes, value-log writes/reads, L0/LSM writes, compaction output, gets, bloom-filter hits, LSM read bytes, and iterator creation.

## Important APIs, Types, And Functions
`clearAllMetrics` iterates over `expvar` variables and resets supported metric types. `TestWriteMetrics` checks user write, put, L0 write, and compaction write metrics. `TestVlogMetrics` checks value-log write/read counters and bytes. `TestReadMetrics` checks get counters, memtable/LSM metrics, bloom-filter map keys, LSM read bytes, and iterator metrics.

## Control Flow
Tests use managed options with close-time compaction, clear global metrics, write random keys/values, inspect expvar counters, sometimes close/reopen to force LSM compaction, then perform reads and missing-key lookups to trigger read metrics.

## State And Persistence Behavior
The metrics are global expvar state, not DB-local state. Some tests perform close/reopen to transition data from memtable/L0 into lower levels and make compaction/LSM metrics observable. Large values are used to force value-log storage.

## Dependencies And Integration Points
The tests depend on metrics functions in `y`, Badger write/read paths, managed write batches, value-log threshold behavior, bloom-filter lookups, close-time compaction, and expvar's process-global registry.

## Risks And Edge Cases
Because expvar is global, test isolation depends on `clearAllMetrics` and no concurrent metric-producing tests. Several byte assertions use `GreaterOrEqual` due to compression/overhead variability. Random data is used to reduce compression effects, but exact sizes remain implementation-sensitive.

## Test Signals
Signals include exact counts for writes, puts, value-log writes/reads, gets, memtable hits, iterator creation, and expected map entries for LSM/bloom metrics after compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/metrics_test.go -->

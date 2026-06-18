# sources/storage-engines/rocksdb/db/merge_test.cc

## Purpose
`merge_test.cc` is the DB-level integration suite for RocksDB merge behavior. It validates merge-based counters through puts, deletes, merges, flushes, compactions, TTL DBs, successive-merge thresholds, partial merge thresholds, manifest concurrency around flush/compaction, `FullMergeV3` compatibility fallback, and oversized merge result rejection.

## Important APIs, types, and functions
`CountMergeOperator` wraps the built-in UInt64Add operator while counting full and partial merge invocations. `EnvMergeTest` wraps the default environment and counts `NowNanos` calls to guard against unnecessary timing overhead. `OpenDb` creates a temporary DB with `CountMergeOperator`, optional TTL, optional `max_successive_merges`, and the counting environment.

`Counters` implements set/remove/get/add using Put/Delete/Get. `MergeBasedCounters` overrides `add` to use DB `Merge`. Helper functions `testCounters`, `testCountersWithFlushAndCompaction`, `testSuccessiveMerge`, `testPartialMerge`, `testSingleBatchSuccessiveMerge`, and `runTest` orchestrate scenarios.

Test cases are `MergeDbTest`, `MergeDbTtlTest`, `MergeWithCompactionAndFlush`, `FullMergeV3FallbackNewValue`, `FullMergeV3FallbackExistingOperand`, `FullMergeV3FallbackFailure`, and `LargeMergeResultRejected`.

## Control flow
Counter tests compare ordinary read-modify-write counters with merge-based counters. They set values, delete missing keys, merge many increments, flush, compact, reopen without merge operator for a negative read check, and verify decoded sums. TTL mode runs the same merge semantics through `DBWithTTL`.

Successive merge tests configure `max_successive_merges` and assert that writes trigger full merge only when the threshold is exceeded, while reads merge the remaining operands. Single-batch tests ensure many merge records in one write batch trigger expected in-mem merge calls and still read back the correct sum.

Partial merge tests flush and compact different operand counts to verify `PartialMergeMulti` is invoked only when operand count reaches the hard-coded minimum and remains below the full-merge threshold. They also confirm no partial merge occurs when a put base exists and that `MergeHelper::FilterMerge` does not call `NowNanos` when detailed timing is disabled.

The flush/compaction concurrency test uses `SyncPoint` callbacks around `VersionSet::LogAndApply` to interleave SetOptions, compaction, background flush, a merge write, and a read. This reproduces a manifest ordering/race scenario and verifies the merged value remains visible.

V3 fallback tests construct merge inputs directly for append, put, and failing operators. They validate no-base, plain-base, wide-column-with-default, and wide-column-without-default cases. The large-result test invokes `MergeHelper::TimedFullMerge` with lazy-zeroed mappings around the 4GB boundary.

## State and persistence behavior
The suite persists data through real DB writes, WAL/memtable state, flushes to SST, compactions, TTL wrappers, MANIFEST updates, and reopen. It observes merge operator call counters and environment timing counters as process-local state. It also validates that an unmerged DB reopened without a merge operator cannot read merge operands as normal values.

## Dependencies and integration points
The test integrates DBImpl, internal formats, merge helper, write batch internals, cache/comparator/env/db/TTL APIs, wide columns, test harness, coding utilities, cast utilities, built-in merge operators, sync points, flush, compaction, SetOptions, and direct `TimedFullMerge`.

## Risks and edge cases
Merge behavior spans memtable reads, compaction, operator compatibility, and recovery. Reopen without merge operator is expected to fail reads where unresolved operands remain. SyncPoint tests depend on internal callback names and old SetOptions manifest behavior restored by a callback. Big-memory tests are skipped when the host lacks enough memory.

## Test signals
Passing this file gives high-level confidence that merge operators work across normal DB writes, TTL DBs, flush/compaction, threshold-triggered full and partial merges, write batches, manifest concurrency, V3 fallback compatibility, wide-column preservation, failure-scope propagation, and 4GB result limits.

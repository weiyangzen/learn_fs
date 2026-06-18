# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTrackerShardEvaluator.cpp

## Purpose
Mock DD workload that runs `DataDistributionTracker` over synthetic mock shard data and records relocation reasons produced by shard evaluation, especially size and write splits.

## Important APIs, types, and functions
`MockDDTrackerShardEvaluatorWorkload` derives from `MockDDTestWorkload`. It owns `DDSharedContext`, `DDMockTxnProcessor`, relocation output and metrics promise streams, `KeyRangeMap<ShardTrackedData>`, actor collection, reason counts, and `DataDistributionTracker`. Key actors are `setup`, `relocateShardReporter`, `start`, and `check`.

## Control flow
Setup builds and populates mock global state and constructs a mock transaction processor. Start launches mock servers, starts a reporter that consumes `RelocateShard` messages and increments `rsReasonCounts`, obtains initial data distribution from the mock processor, builds physical shard and bulk-load collections, constructs a tracker with mock streams and shard map, and runs the tracker for `testDuration`. Check asserts minimum shard count and minimum relocation reason counts, prints counts, clears actors, and returns true.

## State and persistence behavior
All state is mock/in-memory: shard map, mock servers, mock data distribution, and relocation counters. No real database writes occur.

## Dependencies and integration points
Depends on `MockDDTest`, `DDMockTxnProcessor`, `DataDistributionTracker`, physical shard and bulk-load collections, relocation streams, and mock storage metrics APIs.

## Risks and test signals
Risks include tracker behavior depending on synthetic population distributions, wrong-shard-server retries in the reporter, and minimal validation beyond count thresholds. Signals are ASSERTs on shard count and relocation reason counts plus perf metrics named by `RelocateReason`.

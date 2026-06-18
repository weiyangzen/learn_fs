# sources/storage-engines/foundationdb/fdbserver/workloads/SidebandSingle.cpp

## Purpose
`SidebandSingleWorkload` is a single-client variant of the sideband test focused on cached read versions. It validates that `USE_GRV_CACHE` does not return a too-stale result after a sideband signal, including `commit_unknown_result` cases.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `SidebandSingle`. It uses a `PromiseStream<std::pair<uint64_t, Version>>` instead of serialized cross-client interfaces. Core actors are `mutator` and `checker`; the checker sets `FDBTransactionOptions::USE_GRV_CACHE` and initializes shared database state with `cx->initSharedState()`.

## Control Flow
Client 0 runs both actors. The mutator first writes `oldbeef` to a random message key with normal retries, then attempts to write `deadbeef` without retrying `commit_unknown_result`. On unknown result it sends the key with `invalidVersion`; otherwise it sends the committed version. The checker reads the key with GRV cache, requires it to exist, and if it sees a value other than `deadbeef`, compares against a non-cached read to distinguish a legitimately unknown commit result from stale cache behavior.

## State And Persistence Behavior
All state is in normal `Sideband/Message/<key>` keys plus the in-memory promise stream. Old and new values are intentionally written to the same key to create stale-read detection opportunities. Message keys are not removed.

## Dependencies And Integration Points
It depends on NativeAPI transactions, GRV cache transaction option support, shared database state initialization in simulation, and tester metrics. It complements `Sideband.cpp` by removing cross-client request stream serialization from the core GRV-cache test.

## Risks And Edge Cases
The unknown-result path intentionally allows reading `oldbeef` if the no-cache read agrees. If cached and uncached reads differ, it reports `CausalConsistencyError3`. The workload only runs on client 0, so multi-client causality is not covered here.

## Test Signals
`CausalConsistencyError1` reports missing keys, `CausalConsistencyError2` reports stale cached values without unknown-result allowance, and `CausalConsistencyError3` reports cache/no-cache disagreement. `DebugSidebandCheckError` and `DebugSidebandNoCacheError` expose retry paths.

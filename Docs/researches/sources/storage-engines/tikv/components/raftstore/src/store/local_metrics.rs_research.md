# `sources/storage-engines/tikv/components/raftstore/src/store/local_metrics.rs`

## Purpose
This file defines buffered, thread-local raftstore metrics used on the performance-critical path. It converts raftstore events into local Prometheus counters/histograms and flushes them periodically to global collectors, reducing contention in raft pollers and write workers.

## Important APIs, Types, and Functions
- `RaftSendMessageMetrics` wraps `RaftSentMessageCounterVec` and maps raft `MessageType` values to accept/drop counters.
- `HealthStatistics` stores average disk and network latency samples for health inspection. It is backed by private `LocalHealthStatistics`.
- `IoType` distinguishes disk from network health samples.
- `RaftMetrics` owns local counters/histograms for ready handling, message sends/drops, proposals, invalid proposals, raft log GC skips, store/proposal/message timings, peer message size, commit log duration, write-block wait, IO read/write reasons, waterfall metrics, stale-peer checks, and leader-missing tracking.
- `RaftMetrics::new` binds all local metric handles to global metrics from `metrics.rs`.
- `RaftMetrics::maybe_flush` flushes every 10 seconds and updates `LEADER_MISSING`.
- `StoreWriteMetrics` buffers write-worker task wait and waterfall timings.
- `TimeTracker` bridges local histograms with request-level `tracker` TLS metrics and records write-stage timings.

## Control Flow
Pollers create `RaftMetrics::new` with the current waterfall-metrics config. Hot paths increment local handles directly. `maybe_flush` returns early until `METRICS_FLUSH_INTERVAL` has elapsed, then flushes all counters and histograms and drains the `leader_missing` set into a gauge. `RaftSendMessageMetrics::add` explicitly matches raft message types so new raft variants require an instrumentation decision.

`TimeTracker::default` captures the TLS tracker token and records `write_instant` if a tracker is active. `observe` records elapsed duration into the provided local histogram and fills the selected tracker field only once. `reset` moves the local start instant without changing the tracker token.

## State and Persistence Behavior
The file has only in-memory metric buffers. It does not persist raftstore data. The main state risk is observability freshness: local values are not visible globally until a flush interval elapses or an owning component calls flush.

## Dependencies and Integration Points
It depends on Prometheus local metric types, raft `MessageType`, tracker TLS/global trackers, TiKV time utilities, and metric definitions from `metrics.rs`. `RaftMetrics` is embedded in `PollContext` from `fsm/store.rs` and used throughout peer/store FSM code. `StoreWriteMetrics` is used by the async write path. `HealthStatistics` feeds health-controller latency inspectors.

## Risks and Edge Cases
- Message-type matching intentionally ignores internal raft messages; adding a new important raft message without updating this map can hide traffic.
- `HealthStatistics::avg` uses integer microseconds and returns default duration when empty, so zero can mean no samples or truly low latency.
- `leader_missing` uses a mutex-protected set inside `RaftMetrics`; high churn could contend, although it is flushed and cleared periodically.
- Waterfall metrics are conditional, so code must keep config refresh and metric flushing in sync.
- `TimeTracker` only sets tracker fields if they are currently zero, preserving first observation semantics.

## Test Signals
There are no local unit tests. Useful tests would validate `RaftSendMessageMetrics` mapping, flush interval behavior with mocked time, `HealthStatistics` averaging/reset, and `TimeTracker` behavior with and without a TLS tracker token.

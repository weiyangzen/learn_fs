# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvProxyServer.cpp

## Purpose
Implements the GRV proxy role. It accepts `GetReadVersionRequest`s, queues them by priority, enforces ratekeeper limits, asks master/log system for committed read versions, attaches health/throttle/version-vector metadata, and serves global configuration and health metrics.

## Important APIs, Types, and Functions
- `GrvProxyStats` owns counters, queue gauges, rate/limit gauges, latency samples, latency bands, request buckets, and histograms.
- `GrvProxyData` stores the proxy interface, master, request stream, DB info, log system, global config DB handle, latency-band config, version-vector cache, and committed-version tracking.
- `globalConfigMigrate`, `globalConfigRefresh`, and `globalConfigRequestServer` migrate legacy client-info keys and serve cached global config.
- `getRate` polls ratekeeper, updates `GrvTransactionRateInfo`, health metrics, client tag throttles, transaction tag counters, stats, and lease state.
- `queueGetReadVersionRequests` is the intake actor: it handles queue pressure, bounded-delay rejection, stats, and priority queue insertion.
- `transactionStarter` drains queues under normal and batch rate budgets and schedules committed-version/reply actors.
- `getLiveCommittedVersion` confirms epoch liveness when required, asks master for a raw committed version, updates version-vector state, and builds the reply.
- `sendGrvReplies` sends replies, applies min-known-committed-version behavior, tag throttle data, process busy time, mid-shard size, version-vector deltas, and sustained throttling flags.
- `grvProxyServerCore`, `checkRemoved`, and `grvProxyServer` compose and supervise the role.

## Control Flow
Core waits for matching master lifetime and accepting-commits recovery state, builds the log system, starts wait-failure, tracing, transaction starter, health metrics, global config, and optional last-commit updater actors. Intake accepts GRV requests, potentially drops lower-priority work under queue pressure, rejects bounded-delay work before insertion, and schedules the GRV timer. On timer wake, `transactionStarter` starts release windows, selects system/default/batch work until budgets or request limits stop it, splits requests by causal-risky flag, asks for committed versions, and schedules reply senders.

## State and Persistence Behavior
State is mostly in-memory: queues, queued transaction counts, rate budgets, lease state, tag counters/throttles, health snapshots, latency metrics, version-vector cache, global config cache, and committed-version fields. Persistent interactions are global-config migration/refresh transactions and log-system/master committed-version confirmation.

## Dependencies and Integration Points
Integrates `GrvProxyInterface`, commit/GRV request types, master committed-version RPCs, `LogSystem::confirmEpochLive`, ratekeeper, data distributor metrics, `HealthMetricsRequestServer`, `GrvQueueDelay`, `GrvTransactionRateInfo`, global configuration, version vectors, Flow actors, tracing, histograms, and worker failure services.

## Risks and Edge Cases
Queue accounting must stay synchronized across drops, starts, replies, and errors. Bounded-delay rejection depends on estimated remaining delay and lease state. Causal-read-risky grouping skips epoch confirmation. Version-vector reply deltas are conditional and size-sensitive. The code assumes `FLAG_CAUSAL_READ_RISKY == 1`. Global config requests can return `future_version` when cache is stale.

## Test Signals
Covered by GRV proxy unit target, queue-delay helper tests, rate-info throttling test, runtime trace events, code probes, and simulation paths for ratekeeper lease expiry, queue pressure, tag throttling, and master/tlog failures.

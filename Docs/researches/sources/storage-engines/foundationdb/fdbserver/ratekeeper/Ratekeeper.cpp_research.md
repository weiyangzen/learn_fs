# sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.cpp

Purpose: implements the ratekeeper role that computes transaction-per-second limits for default and batch priorities from storage-server queues, tlog queues, disk space, version lag, durability lag, recovery state, and tag throttling.

Important APIs and functions: `Ratekeeper::run` composes actors for configuration, storage/tlog metric tracking, tag throttle monitoring, hot-shard throttling, commit-cost collection, DBInfo changes, and rate updates. `handleGetRateInfoReqs` returns per-proxy TPS leases and pushed tag throttle maps. `updateRate` is the core limiter algorithm. `StorageQueueInfo::update`, `refreshCommitCost`, and `TLogQueueInfo::update` maintain smoothed metrics. `getSSVersionLag` separates primary and remote DC versions. The free `ratekeeper` actor starts the role.

Control flow, state, and persistence: state is in-memory maps keyed by server UID, `Smoother` counters, proxy leases, health metrics, and recovery windows. Persistent reads/watches use system keys for configuration and tag throttles through `Database`; no local files are written. The role periodically polls metric endpoints and recomputes limits every metric interval.

Dependencies and integration: consumes `ServerDBInfo`, `StorageServerInterface`, `TLogInterface`, `RatekeeperInterface`, failure monitoring, system configuration keys, `TagThrottler`, and health metrics sent to proxies. It also talks to commit proxies for hot-shard throttling.

Risks and test signals: risks include over-throttling when server-list fetches stall, smoothing reset on instance changes, division by small input rates, remote-DC filtering mistakes, and incorrect ignored-zone logic. Signals are `RkUpdate*` traces, health metrics, tag throttle counts, storage/tlog queue limits, and tests or simulation assertions around server-list consistency and recovery transitions.

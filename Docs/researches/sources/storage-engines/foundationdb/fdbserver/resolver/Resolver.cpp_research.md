# sources/storage-engines/foundationdb/fdbserver/resolver/Resolver.cpp

Purpose: implements the resolver actor that serializes commit-batch conflict resolution, tracks recent metadata state transactions, serves resolution split/metric requests, and optionally applies resolver-private metadata mutations.

Important APIs and functions: `Resolver` owns conflict state, recent state transaction cache, proxy request history, sampling metrics, optional log-system-backed `txnStateStore`, key-server cache, and counters. `resolveBatch` enforces per-proxy ordering with `versionReady`, detects conflicts through `ConflictBatch`, records committed/too-old/conflicted statuses, stores state transactions, emits private mutations, updates TLog previous-commit-version maps, and responds idempotently to duplicate requests. `resolveMetricsRequests`, `resolveSplitRequests`, `pollMetrics`, and transaction-state request processing support resolution balancing and recovery. `resolverCore` initializes logsystem consumers and actor streams.

Control flow, state, and persistence: resolver state is mostly memory-resident. When private resolver mutations are enabled, a `LogSystemDiskQueueAdapter` and `IKeyValueStore` hold transaction-state metadata recovered from `TxnStateRequest` parts. Recent state transactions are retained until all commit proxies have advanced.

Dependencies and integration: integrates with commit proxies through `ResolverInterface`, master through initialization, logsystem, metadata mutation application, storage info caches, version-vector unicast, histograms, and failure monitoring.

Risks and test signals: risks include proxy ordering deadlocks under memory pressure, duplicate reply retention, state transaction cache growth, private mutation divergence from commit proxy logic, and recovery request sequencing. Signals are resolver counters/histograms, conflict outcomes, state byte limits, resolution metrics, and worker removal termination traces.

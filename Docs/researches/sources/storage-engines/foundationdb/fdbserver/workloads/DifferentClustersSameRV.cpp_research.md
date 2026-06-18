# sources/storage-engines/foundationdb/fdbserver/workloads/DifferentClustersSameRV.cpp

Purpose: Implements a multi-cluster simulation workload that probes behavior when two different clusters are read at the same read version and when a connection record switches from one cluster to another.

Important APIs/types/functions: `DifferentClustersSameRVWorkload`, `Database::createSimulatedExtraDatabase`, `_setup`, `advanceVersion`, `doSwitch`, `readerClientSeparateDBs`, `writerClient`, `ClusterConnectionMemoryRecord`, `lockDatabase`, `unlockDatabase`, `runRYWTransaction`, and `minRequiredCommitVersionKey`.

Control flow: Setup advances both original and extra cluster versions to a common high floor. Start launches concurrent separate-cluster readers, a delayed switch actor, and writers on both clusters. `doSwitch` sets a watch, locks both DBs, reads a value/version from the original, copies it to the extra DB, advances the extra DB past that version, switches the connection record, verifies a read at the old version returns the same value or a retryable error, unlocks the extra DB, writes the watched key, waits for the watch, and finally unlocks the original.

State and persistence behavior: Both clusters mutate `keyToRead`; the extra cluster also gets `keyToWatch`. System state is touched through database locks and `minRequiredCommitVersionKey`. Runtime state records `switchComplete`.

Dependencies/integration: Requires exactly one simulated extra database, lock-aware transactions, connection-record switching, watches, and Flow error tracing.

Risks: The workload assumes simulated extra database configuration. Watch completion and old-version reads are timing-sensitive. Errors are generally passed through `onError`, but failure to complete the switch fails `check`.

Test signals: `DifferentClusters_*` trace milestones, reader code probe for different values at same version across clusters, watch completion, and absence of `DifferentClustersSwitchNotComplete`.

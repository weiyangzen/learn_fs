# sources/storage-engines/foundationdb/fdbserver/datadistributor/include/fdbserver/datadistributor/MockGlobalState.h

Purpose: declares the in-memory mock storage cluster used by DD tests. It models shard status, server-key state, key-location service behavior, topology, process locality, storage metrics service endpoints, and simple read/write/clear operations.

Important APIs and types: `MockShardStatus` and `isStatusTransitionValid()` define shard lifecycle. `MockStorageServer` implements `IStorageMetricsService` with `ShardInfo`, `FetchKeysParams`, disk/cpu constants, server key map, byte samples, storage interface, data operations, metrics RPC handlers, fetch signaling, and protected split/sample helpers. Mock topology is represented by `mock::TopologyObject` and `mock::Process`. `MockGlobalState` implements `IKeyLocationService`, owns `shardMapping`, `allServers`, configuration, topology, workload knobs, cluster initialization, server addition, source/destination checks, metric wait/split, key-location lookup, data ops, and server-running helpers.

Control flow: callers build topology with `initializeClusterLayout()`, initialize seed storage with `initializeAsEmptyDatabaseMGS()`, optionally add storage per process, then run mock servers. DD mock transaction code uses `shardMapping` and `allServers` to answer source-server queries and drive moves. `MockStorageServer` methods mutate `serverKeys`, samples, counters, and disk usage in response to simulated operations and fetch completion.

State and persistence: all state is transient. `MockGlobalState::g_mockState()` offers a process-global shared pointer. The mock deliberately mirrors production system key concepts in memory: `keyServers` as `shardMapping`, `serverListKeys` as `allServers`, and `serverKeys` per mock storage server.

Dependencies and integration: depends on storage metrics, key range maps, storage server interfaces, database configuration, key-location service, shard/team failure mapping, and simulated-cluster config. It is the backing state for `DDMockTxnProcessor` and `MockDataDistributor`.

Risks: default public workload fields such as `emptyProb`, `minByteSize`, and `maxByteSize` are not initialized in the constructor and must be set before use in workloads that depend on them. Mock behavior is intentionally approximate: simplified locality, simplified disk/CPU model, and mostly single-region assumptions. Status and server-removal contracts are documented but enforced by assertions rather than durable invariants.

Test signals: the implementation file contains tests for initialization, shard splitting, status transitions, locations, metrics, and data operations. Additional tests should cover uninitialized workload knobs, failed-server contracts, mock server removal, and source/destination checks during in-flight moves.

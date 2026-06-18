# sources/object-store/garage/src/table/replication/parameters.rs

Purpose: defines the replication strategy contract used by all table operations and synchronization workers.

Important APIs and types: `TableReplication` trait defines associated `WriteSets`, anti-entropy interval, storage nodes, read nodes/quorum, write sets/quorum, partition lookup, and sync partition listing. `SyncPartitions` packages a layout version and list of `SyncPartition`s. `SyncPartition` contains the partition ID, first/last hash bounds, and storage node sets.

Control flow: concrete implementations use the trait to direct reads, writes, Merkle partitioning, offload, anti-entropy, and layout sync progress. `WriteSets` must be both `AsRef` and `AsMut` over `Vec<Vec<Uuid>>` and is usually a layout `WriteLock`, ensuring writes delay layout acknowledgment until complete.

State and persistence: no state; this is a contract. Implementations read layout state and persistent table workers use the results.

Dependencies and integration: bridges `garage_rpc::layout` with table data/sync/GC. All table replication modes must provide partition ranges for `TableSyncer`.

Risks and test signals: trait semantics are stronger than type signatures: write sets must include all active layout versions when needed, and quorums must match the consistency model. Incorrect implementations can silently corrupt replication. No tests here; fullcopy/sharded and table integration validate behavior.

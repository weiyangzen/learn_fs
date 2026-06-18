# sources/object-store/garage/src/table/replication/sharded.rs

Purpose: `TableReplication` implementation for ring-sharded tables, where each partition is stored on the nodes assigned by the current and active layout versions.

Important APIs and types: `TableShardedReplication` holds a `LayoutManager` and `ConsistencyMode`. It implements storage/read nodes, quorums, write sets, partition mapping, and sync partition generation.

Control flow: `storage_nodes` unions nodes for the hash across all active versions, deduplicating for layout transitions. `read_nodes` uses the `read_version` selected by layout sync trackers. `read_quorum` and `write_quorum` delegate to read/current layout version quorum methods. `write_sets` obtains a layout `WriteLock` over one node set per active layout version. `sync_partitions` enumerates current layout partitions, sets hash ranges by adjacent partition starts, and attaches write sets for each partition.

State and persistence: no local persistence. Runtime access to layout state is protected by `LayoutManager`; write operations hold `WriteLock` to delay ack advancement.

Dependencies and integration: used by large Garage metadata/data tables where ownership follows the layout ring. Depends on layout version partition and node assignment functions.

Risks and test signals: during layout transitions, all active write sets must be written to avoid losing data. `partition_of` uses current layout, which is correct for Merkle partitioning but sensitive during transitions. Tests are indirect through layout assignment and table sync/offload.

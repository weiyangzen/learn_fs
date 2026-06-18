# sources/object-store/garage/src/table/replication/fullcopy.rs

Purpose: `TableReplication` implementation for small fully replicated tables, where every layout node stores every entry.

Important APIs and types: `TableFullReplication` stores `Arc<System>` and `ConsistencyMode`. It implements storage/read nodes, read/write quorum calculation, write sets, partition mapping, and sync partition enumeration.

Control flow: `storage_nodes` returns all layout nodes across the current cluster layout. `read_nodes` uses the layout's `read_version` all nodes. In consistent mode, read quorum is majority of read-version nodes; dangerous/degraded reads need one. `write_sets` returns one all-node set for each active layout version under a layout write lock. Write quorum is majority-like across active versions, with a warning and fallback if active layouts have very different node counts. Sync treats the entire table as partition `0` over the full hash range.

State and persistence: no persistence here. It reads layout state from `System` and participates in ack-locking through `WriteLock`.

Dependencies and integration: used by tables that are small enough to store on gateways and storage nodes. Tightly coupled to `System::cluster_layout` and layout history.

Risks and test signals: comments note layout tracking is harder because gateway nodes store this data but are not storage nodes for sharded data. If writes fail, nodes can read outdated data. The warning path for mismatched active layout sizes indicates possible quorum degradation. No direct tests in file.

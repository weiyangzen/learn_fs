# sources/object-store/garage/src/table/sync.rs

Purpose: table anti-entropy and layout-transition synchronization. It compares Merkle trees with peers, pushes missing/different items, offloads partitions the local node no longer owns, and reports table sync progress to the layout manager.

Important APIs and types: `TableSyncer<F, R>` owns `System`, `TableData`, `MerkleUpdater`, an optional full-sync trigger channel, and `SyncRpc` endpoint. `SyncRpc` includes root checksum, node fetch, item transfer, and OK messages. `SyncWorker` tracks layout digest, full-sync scheduling, and partition todo list.

Control flow: workers add full syncs on manual trigger, layout digest changes, or `R::ANTI_ENTROPY_INTERVAL`. `sync_partition` checks whether this node is in any storage set. If yes, it syncs with every node in the partition's write sets and validates quorum through `QuorumSetResultTracker`; if no, it offloads all local items in the hash range to current storage nodes and compare-deletes local copies. Driver-side sync checks remote root Merkle hash, walks differing intermediate nodes, queues leaf values, and sends items in batches. Receiver-side RPCs compare root hashes, return Merkle nodes, and merge received items into `TableData`.

State and persistence: persistent state lives in table store and Merkle trees. Worker state is in-memory. Completing all partitions calls `layout_manager.sync_table_until` with the sync partition layout version.

Dependencies and integration: combines table replication, Merkle updater, RPC helper, system layout notifications, metrics, background workers, and Tokio channels.

Risks and test signals: Merkle trees may lag writes; code logs and tolerates missing/mismatched values. Offload requires all target nodes and can retry changed rows. Layout digest changes reset sync work. No direct unit tests; correctness is integration-level and central to safe layout changes.

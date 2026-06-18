# sources/object-store/garage/src/rpc/layout/manager.rs

Purpose: runtime owner of cluster layout state. It loads and saves layout history, merges advertised layouts and trackers, broadcasts updates, and provides write locks that coordinate layout acknowledgments with table writes.

Important APIs and types: `LayoutManager::new`, `layout`, `update_cluster_layout`, `add_table`, `sync_table_until`, `write_lock_with`, `handle_advertise_status`, pull/advertise handlers, and `WriteLock<T>`. Fields include local node ID, replication factor, `Persister<LayoutHistory>`, `RwLock<LayoutHelper>`, change `Notify`, per-table sync versions, `RpcHelper`, and system endpoint.

Control flow: initialization loads `cluster_layout`, validates replication factor compatibility, or creates a fresh history. It wraps it in `LayoutHelper`, updates local trackers, and builds `RpcHelper`. Advertised status digests trigger async pulls for full layouts or tracker-only updates. Merge functions write-lock the helper, merge valid incoming state, update local trackers, notify waiters, broadcast the new state, and save asynchronously. `sync_table_until` computes the minimum sync version across registered tables and advertises tracker progress.

State and persistence: persists `cluster_layout` under the metadata directory. Runtime state includes table sync progress and ack-lock counters. `WriteLock` increments the current layout's lock count; its `Drop` decrements and may advance local ack when all older writes finish.

Dependencies and integration: connects `SystemRpc`, `RpcHelper`, `PeeringManager`, `Persister`, `LayoutHelper`, and table replication write sets.

Risks and test signals: replication-factor mismatch aborts layout reuse for safety. `WriteLock::drop` unwraps `current`, so layout invalidity during drop would be serious. Async broadcast/save errors are logged. Tests are indirect through layout and table write/sync paths.

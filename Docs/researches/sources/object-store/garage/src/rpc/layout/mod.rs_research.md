# sources/object-store/garage/src/rpc/layout/mod.rs

Purpose: layout module root. It defines persisted layout data types, migration formats, constants, re-exports, and CRDT helpers.

Important APIs and types: re-exports `LayoutHelper`, `RpcLayoutDigest`, `SyncLayoutDigest`, `WriteLock`, and all current version types. Constants include `PARTITION_BITS = 8`, `NB_PARTITIONS = 256`, `CompactNodeType = u8`, and `MAX_NODE_NUMBER = 256`. Current `v010` types are `LayoutHistory`, `LayoutVersion`, `LayoutStaging`, `UpdateTrackers`, and `UpdateTracker`; older `v08` and `v09` modules define migration inputs.

Control flow and migrations: `v09::ClusterLayout::migrate` converts old arbitrary capacity units to bytes, derives partition size from old assignment data, introduces `LayoutParameters`, and creates staging fields. `v010::LayoutHistory::migrate` wraps the old cluster layout into a one-version history and initializes ack/sync/sync-ack trackers for storage nodes. Utility CRDT implementations make layout parameters and node roles warn on divergence, while `LayoutStaging::merge` merges parameters and roles.

State and persistence: the current data structures are serialized to disk by `Persister<LayoutHistory>`. `node_id_vec` ordering deliberately places storage nodes before gateways so compact assignment bytes can index storage nodes efficiently.

Dependencies and integration: consumed by RPC layout manager, table replication, system metrics, and admin layout commands. Uses `garage_util` CRDT/data migration facilities.

Risks and test signals: compact node IDs cap non-gateway storage nodes at 256. Migration capacity scaling is explicitly arbitrary and may be inaccurate for old deployments. A duplicated `versions` field appears in the shown `v010::LayoutHistory` block and would be a compile concern if present in the active source. Layout tests validate assignment behavior.

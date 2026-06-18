# sources/object-store/garage/src/rpc/layout/helper.rs

Purpose: cached, validated wrapper around persisted `LayoutHistory`. It computes fast-read layout views, synchronization digests, and local update tracker changes.

Important APIs and types: `RpcLayoutDigest` advertises current layout version, active version count, tracker hash, and staging hash. `SyncLayoutDigest` tracks fields relevant to table sync. `LayoutHelper` owns an optional `LayoutHistory`, consistency mode, cached ack/sync minima, all nodes, storage nodes, hashes, validity flag, and `ack_lock` counters keyed by layout version.

Control flow: `new` optionally collapses history to the current version for non-consistent modes, prunes old versions, computes all node sets, clamps update trackers, calculates `ack_map_min` and quorum-aware `sync_map_min`, hashes trackers/staging, retains active ack locks, and records whether `layout.check()` passed. `update` is the only mutation wrapper: it applies a closure to `LayoutHistory` and rebuilds all caches if changed. `current`, `versions`, `read_version`, `all_nodes`, and `all_nongateway_nodes` refuse access when layout checks fail.

State and persistence: no direct disk IO, but it wraps the state persisted by `LayoutManager`. The ack lock blocks acknowledging a newer layout while local writes still use an older version.

Dependencies and integration: central to `LayoutManager`, table replication read/write sets, system status exchange, and sync scheduling. Uses Garage CRDT/data/error types and replication consistency modes.

Risks and test signals: `update_ack_to_max_free` is subtle because a wrong ack can let the cluster prune an old layout while writes are still in flight. Read-version selection depends on sync trackers and quorums. Tests are indirect through layout/history/table sync behavior.

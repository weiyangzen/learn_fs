# sources/object-store/garage/src/rpc/layout/history.rs

Purpose: layout history lifecycle and CRDT merge logic for active, old, and staged cluster layouts.

Important APIs and functions: `LayoutHistory::new`, `current`, `min_stored`, `get_all_nodes`, `get_all_nongateway_nodes`, `keep_current_version_only`, `cleanup_old_versions`, `clamp_update_trackers`, `calculate_sync_map_min_with_quorum`, `calculate_trackers_hash`, `calculate_staging_hash`, `merge`, `apply_staged_changes`, `revert_staged_changes`, and `check`.

Control flow: cleanup removes invalid leading versions when a later current layout is valid, moves active versions to `old_versions` once current nodes have sync-acked beyond them, and caps `old_versions` at `OLD_VERSION_COUNT`. Sync-map calculation returns the current version for single-version histories, uses the global min when writes require all replicas, and otherwise evaluates write sets by partition to find a safe read version under quorum rules. `merge` appends next versions, checks conflicting same-version layouts, merges update trackers, and merges staged CRDT changes. `apply_staged_changes` computes the next `LayoutVersion`, pushes it, cleans up, and clears staged role changes while preserving parameters.

State and persistence: `LayoutHistory` is the persisted object saved as `cluster_layout` by `LayoutManager`. Trackers determine when old versions are safe to retire.

Dependencies and integration: uses CRDT `Lww`/`LwwMap`, nonversioned encoding for hashes, replication factors, and `ComputationStat` from `version.rs`. Table sync reports progress back into these trackers.

Risks and test signals: history merge assumes linear version increments and logs conflicts instead of resolving divergent same-version layouts. Wrong tracker math can break read-after-write consistency. Assignment tests exercise staged changes; broader tracker behavior is mostly integration-tested by cluster operation.

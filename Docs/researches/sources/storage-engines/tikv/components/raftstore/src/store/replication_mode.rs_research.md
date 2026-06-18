# sources/storage-engines/tikv/components/raftstore/src/store/replication_mode.rs

## Purpose
`replication_mode.rs` tracks global replication-mode metadata and maps stores into commit groups for disaster-recovery auto-sync mode. It lets raftstore calculate per-peer group ids from store labels while preserving labels across majority-mode periods.

## Important APIs, Types, and Functions
`StoreGroup` is the main registry. It stores backed-up labels by store id, label-value to group-id mapping, store-id to group-id mapping, active label key, current version/state id, and a dirty flag. Key methods are `backup_store_labels`, `register_store`, `group_id`, and private `recalculate`.

`GlobalReplicationState` wraps the current `ReplicationStatus`, a public `StoreGroup`, and a reusable `group_buffer`. It exposes `status`, `set_status`, `calculate_commit_group`, and `store_dr_autosync_status`.

## Control Flow
When the system is in majority mode, `backup_store_labels` can save a store's labels after taking them from the store object. If the saved labels are unchanged it does nothing; otherwise it marks the registry dirty. `register_store` associates a live store with labels. If the store is already registered, the same label key must map to the same group id or the function panics. If the store is new and the active label key exists in its labels, the label value is assigned an existing or new group id and the store is mapped to it. Stores missing the active label key can be known in `labels` but have no group id.

`set_status` stores a new PD replication status and calls `StoreGroup::recalculate`. Recalculation is skipped in majority mode and skipped when label key and dirty flag are unchanged. Otherwise, the new DR state id must increase, caches are cleared, the active label key and version are updated, and every saved store label is scanned to rebuild store/group mappings.

`group_id(version, store_id)` returns no group when the caller's version is older than the registry version, preventing regions computed under older label keys from mixing with newer group assignments. `calculate_commit_group` clears and reuses `group_buffer`, walking region peers and adding `(peer_id, group_id)` for peers whose store currently has a group id. `store_dr_autosync_status` exposes only the DR auto-sync state/state-id subset when the mode is `DrAutoSync`.

## State and Persistence Behavior
This module is in-memory state. Durability comes from external PD/store metadata feeds, not from local persistence here. The `version` field is the DR auto-sync state id and gates stale calculations. The dirty flag makes label backups visible to the next recalculation even if the label key did not change.

## Dependencies and Integration Points
The module depends on `kvproto::metapb` stores/peers and `replication_modepb` mode/status messages. It integrates with store heartbeat or PD status update paths that call `set_status`, store registration paths that call `register_store` or `backup_store_labels`, and raft proposal/commit logic that needs commit groups for a region's peer set.

## Risks and Edge Cases
Several invalid state transitions intentionally panic: recalculating with a non-increasing state id, registering an already grouped store with labels that imply a different group, or registering an already grouped store without the active label key. Group ids are assigned by `HashMap`/insertion progression over stored labels, so tests should guard expected behavior but external code should not depend on stable ids beyond a given process/state calculation. Switching back to majority mode does not clear cached group ids, by design, so callers must respect mode/version semantics.

## Test Signals
`test_group_register` verifies delayed group assignment before DR status, grouping by zone labels, adding stores after calculation, majority-mode preservation, recalculation with newer state ids, and label-key switch to host. `test_backup_store_labels` verifies backup while labels are taken from stores, dirty-triggered recalculation, stores without group ids later updating labels, and panic on attempts to change a calculated group id.

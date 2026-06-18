# sources/object-store/rustfs/crates/ecstore/src/client/object_handlers_common.rs

## Purpose
Provides shared object-handler logic for lifecycle cleanup of noncurrent object versions, including delete replication scheduling.

## Important APIs, types, and functions
`delete_object_versions` is the main exported async function. `lifecycle_version_delete_replication_state` builds `ReplicationState` with purge-target status derived from replication pending status.

## Control flow
The function first reads bucket versioning state. It processes input deletes in chunks capped by `MAX_DELETE_LIST`. For each object, it fetches object info and asks replication policy whether the delete should be replicated. It then calls `ECStore::delete_objects`; successful deleted objects with replication candidates receive replication state and are scheduled through `schedule_replication_delete`. Per-object failures are logged with lifecycle context.

## State and persistence behavior
Persistent object/version state is modified through `ECStore::delete_objects`. Replication state is attached to deleted-object records and handed to the replication scheduler. The module itself stores no local state.

## Dependencies and integration points
It integrates lifecycle events, bucket versioning system, replication decision/scheduling, `ECStore`, object options, file metadata replication state, and lock limits. It is a bridge between lifecycle expiration and replication subsystems.

## Risks and edge cases
If bucket versioning config or object info lookup fails, cleanup for affected items is skipped and only debug logged. Replication decisions are made before deletion; object state can change between lookup and delete. Error indexing assumes returned `deleted_objs` and `errors` align with the current batch.

## Test signals
A unit test verifies replication state preserves pending purge target maps and the original replicate decision string. Broader behavior requires integration tests around lifecycle deletion, versioning suspended/enabled states, and replication scheduling.

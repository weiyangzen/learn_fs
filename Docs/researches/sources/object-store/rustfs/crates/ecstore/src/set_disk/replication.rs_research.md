# sources/object-store/rustfs/crates/ecstore/src/set_disk/replication.rs

## Purpose
Provides a metadata-only restore helper for transitioned/restored objects. It removes the `x-amz-restore` marker from user metadata by issuing an in-place copy.

## Important APIs, Types, And Functions
`SetDisks::update_restore_metadata(bucket, object, obj_info, opts)` clones `ObjectInfo`, sets `metadata_only = true`, removes `X_AMZ_RESTORE` from `user_defined`, preserves the version ID, and calls `copy_object` from the object to itself with source and destination `ObjectOptions`.

## Control Flow
The method constructs a mutable metadata-only object info value, mutates user metadata through `Arc::make_mut`, derives `version_id`, and delegates all persistence and quorum behavior to the normal copy-object path. The `_opts` parameter is currently unused.

## State And Persistence Behavior
Persistent state changes are indirect: the in-place copy updates object metadata on the erasure set without rewriting object data when the copy path honors `metadata_only`.

## Dependencies And Integration Points
It depends on the object copy implementation, `ObjectInfo`, `ObjectOptions`, and the S3 restore metadata key constant. It is likely used by lifecycle/tier restore flows after a restored object’s expiry metadata changes.

## Risks
Correctness is delegated to `copy_object`; if metadata-only handling changes there, restore metadata updates may rewrite data or mishandle versions. The ignored `_opts` may hide caller intent such as locking or preconditions.

## Test Signals
No tests in this file. Useful coverage would assert that restore metadata is removed for a specific version and that other user metadata and object data are preserved.

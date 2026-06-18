# sources/object-store/rustfs/crates/e2e_test/src/delete_objects_versioning_test.rs

## Purpose
This regression suite verifies that `DeleteObjects` on a versioned bucket creates delete markers that are immediately visible through `ListObjectVersions`. It targets issue #1878, where metadata updates could be temporarily invisible and listings could still report the old object version as latest.

## Important APIs, Types, and Functions
The tests use AWS SDK S3 `put_bucket_versioning`, `put_object`, `delete_objects`, and `list_object_versions`, with `BucketVersioningStatus::Enabled`, `VersioningConfiguration`, `Delete`, and `ObjectIdentifier`.

## Control Flow
The single-key test creates a bucket, enables versioning, uploads an object, verifies one latest version and no markers, calls plural `delete_objects` without a version id, captures the returned delete-marker version id, immediately lists versions, and checks one latest delete marker plus the original non-latest version. The multiple-key test uploads three keys, deletes all in a single request, immediately lists versions, and asserts every key has a latest delete marker.

## State and Persistence
State includes versioned bucket metadata, object versions, delete markers, and `xl.meta` visibility in the RustFS backend. The tests intentionally do not sleep between delete and list, making immediate metadata visibility the persistence property under test.

## Dependencies and Integration Points
The file integrates versioned delete semantics, batch delete response generation, metadata write/rename visibility, file-cache invalidation, and list-object-versions consistency.

## Risks and Edge Cases
The tests do not cover quiet delete mode, partial failures, explicit version-id deletes, suspended versioning, or many-key pagination. They use fixed bucket names and require serial execution.

## Test Signals
Signals include returned `delete_marker=true`, returned delete-marker version id, exactly one marker immediately after delete, marker `is_latest=true`, original version `is_latest=false`, and all three markers visible after a multi-key delete.

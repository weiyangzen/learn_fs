# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManagerImpl.java

## Purpose

`BucketManagerImpl` is the read/ACL implementation of `BucketManager` backed by `OMMetadataManager`.

## Important APIs and Types

- Constructor stores `OzoneManager` and `OMMetadataManager`.
- `getBucketInfo` reads bucket metadata under the bucket read lock.
- `listBuckets` delegates to `metadataManager.listBuckets`.
- `getAcl` validates bucket resource type, reads `OmBucketInfo`, and returns bucket ACLs.
- `checkAccess` optionally resolves bucket links, reads bucket ACLs, and evaluates them through `OzoneAclUtil.checkAclRights`.

## Control Flow

`getBucketInfo` validates arguments, acquires `BUCKET_LOCK`, calls `OzoneManagerUtils.getBucketInfo`, logs unexpected IOExceptions, and releases the lock. `getAcl` rejects non-bucket `OzoneObj`s, acquires the bucket lock, looks up the bucket table row by metadata key, throws `BUCKET_NOT_FOUND` if absent, and returns ACLs. `checkAccess` decides whether to resolve bucket links: bucket operations are resolved except DELETE, READ_ACL, and READ, while KEY and PREFIX resources are resolved. It then locks the resolved bucket, loads metadata, throws not-found when absent, checks ACL rights, logs debug results, and converts unexpected IO failures to `OMException(INTERNAL_ERROR)`.

## State and Persistence

The implementation is stateless beyond references to OM and metadata manager. It reads persisted bucket rows from OM metadata tables but does not mutate them.

## Dependencies and Integration Points

It integrates with `OzoneManager.resolveBucketLink`, `OMMetadataManager` locking/tables, `OzoneManagerUtils`, `OmBucketInfo`, `OzoneAclUtil`, `OzoneObj`, `RequestContext`, and OM exception result codes.

## Risks and Edge Cases

The link resolution rules are subtle: some bucket ACL checks intentionally operate on the source/link bucket, while writes/key/prefix checks resolve to the real bucket. If resolution fails with bucket-not-found, the code logs a warning and continues to check the original bucket; other errors become internal errors. Non-OM exceptions are logged, but OM exceptions are passed through. Correct lock release depends on all paths reaching `finally`, which the code does.

## Test Signals

Tests should cover get/list behavior, missing bucket errors, non-bucket `getAcl` rejection, ACL success/failure, link bucket resolution for key/prefix and selected bucket operations, and lock release on exceptions.

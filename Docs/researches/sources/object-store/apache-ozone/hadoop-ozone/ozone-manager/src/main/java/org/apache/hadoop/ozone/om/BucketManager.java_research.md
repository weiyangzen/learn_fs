# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/BucketManager.java

## Purpose

`BucketManager` defines the OM bucket-level management interface and extends ACL checking via `IOzoneAcl`.

## Important APIs and Types

- `getBucketInfo(volumeName, bucketName)` returns `OmBucketInfo`.
- `listBuckets(volumeName, startBucket, bucketPrefix, maxNumOfBuckets, hasSnapshot)` returns a paged list of `OmBucketInfo` for a volume, optionally filtered by prefix and snapshot presence.
- Inherited ACL methods are `getAcl` and `checkAccess`.

## Control Flow

This is an interface; implementation flow is in `BucketManagerImpl` and other possible implementations.

## State and Persistence

The interface describes access to bucket metadata persisted in OM metadata storage but holds no state.

## Dependencies and Integration Points

It depends on `OmBucketInfo`, `IOException`, and `IOzoneAcl`. OM request handlers use this abstraction for bucket reads/listings and ACL checks.

## Risks and Edge Cases

Interface semantics require callers and implementations to agree on pagination exclusivity, prefix filtering, snapshot filtering, and whether bucket links are resolved.

## Test Signals

Contract tests should cover get, list pagination, prefix filtering, snapshot filtering, and ACL behavior through concrete implementations.

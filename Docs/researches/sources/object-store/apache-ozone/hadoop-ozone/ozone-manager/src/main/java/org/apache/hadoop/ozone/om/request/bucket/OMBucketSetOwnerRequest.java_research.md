# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetOwnerRequest.java

## Purpose

`OMBucketSetOwnerRequest` handles the owner-change variant of `SetBucketProperty`. It updates only the owner and modification/update metadata for an existing bucket.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` stamps the set-bucket-property request with current modification time and user info.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` validates the owner field, checks `WRITE_ACL`, loads the bucket, handles no-op same-owner requests, updates `OmBucketInfo.owner`, and emits `OMBucketSetOwnerResponse`.

## Control Flow And State

The method rejects requests without `ownerName` as `INVALID_REQUEST` before acquiring locks. For valid input it increments bucket-update metrics, acquires the bucket write lock, reads the bucket row, rejects missing buckets, compares old owner, and either returns a no-op response with `success=false` but status `OK`, or writes a new bucket cache entry with updated owner, modification time, and update ID. Audit logging occurs outside the lock.

## Dependencies And Integration Points

It uses `SetBucketPropertyRequest/BucketArgs`, `OmBucketArgs` audit conversion, bucket table cache writes, OM ACL checks, `OMBucketSetOwnerResponse`, and OM metrics.

## Risks And Test Signals

The unusual same-owner path returns status OK while marking response false, so client behavior should be tested. Other tests should cover missing owner, missing bucket, ACL denial, null old owners from pre-HDDS-6171 metadata, modification time propagation from preExecute, cache update IDs, and failure metric increments.

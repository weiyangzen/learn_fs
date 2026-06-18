# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/RegularBucketLockStrategy.java

## Purpose
`RegularBucketLockStrategy` is the standard `OzoneLockStrategy` for non-FSO bucket operations. It validates the target bucket and acquires/releases `OzoneManagerLock.LeveledResource.BUCKET_LOCK`.

## Important APIs and Types
It implements `acquireWriteLock`, `releaseWriteLock`, `acquireReadLock`, and `releaseReadLock`. All methods take `OMMetadataManager`, volume, bucket, and key names, but the key name is unused for regular bucket locking.

## Control Flow
Acquire paths call `OMFileRequest.validateBucket(omMetadataManager, volumeName, bucketName)` before acquiring the bucket lock from `omMetadataManager.getLock()`. Release paths delegate directly to the matching `release*Lock(BUCKET_LOCK, volumeName, bucketName)`.

## State and Persistence Behavior
The class has no state and does not persist. It protects metadata reads and writes performed after validation by taking the bucket-level lock.

## Dependencies and Integration Points
It integrates with `OMMetadataManager`, `OMFileRequest.validateBucket`, `OzoneLockStrategy`, and `OzoneManagerLock`. It is a strategy slot for code that chooses lock behavior based on bucket layout or request type.

## Risks and Edge Cases
Validation happens before lock acquisition, so bucket state can theoretically change between validation and lock acquisition unless outer code holds a broader lock. Release does not validate and assumes the caller owns the lock.

## Test Signals
Tests should cover validation failure, read/write acquisition and release against `BUCKET_LOCK`, and behavior when volume/bucket names select the same stripe.

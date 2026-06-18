# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/OBSKeyPathLockStrategy.java

Purpose: `OBSKeyPathLockStrategy` is the object-store bucket lock strategy that combines a bucket read lock with a key-path read or write lock. It allows finer-grained key locking while keeping bucket metadata stable.

Important APIs and types: It implements `OzoneLockStrategy` methods for read/write acquire and release. It uses `BUCKET_LOCK`, `KEY_PATH_LOCK`, `OMMetadataManager`, `OMFileRequest.validateBucket`, `OMLockDetails`, and Guava `Preconditions`.

Control flow: Acquire methods first validate the bucket, acquire a bucket read lock, assert acquisition, then acquire the key-path lock and merge lock details. Release methods release the key-path lock first, then the bucket read lock, merging details.

State and persistence behavior: The strategy stores no state. It coordinates in-memory lock state around persistent key-table or file-table operations.

Dependencies and integration points: `OzoneLockProvider` chooses this strategy for object-store buckets and some legacy buckets when key-path locking is enabled.

Risks and test signals: If key-path lock acquisition fails after bucket lock acquisition, the current method does not explicitly release the bucket lock before propagating. Tests should cover successful read/write lock pairs, bucket validation failure, release order, merged lock details, and failure injection during second lock acquisition.

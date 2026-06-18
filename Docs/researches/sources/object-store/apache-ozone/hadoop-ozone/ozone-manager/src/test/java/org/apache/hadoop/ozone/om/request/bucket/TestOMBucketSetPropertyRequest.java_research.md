# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketSetPropertyRequest.java

Tests `OMBucketSetPropertyRequest` for versioning, quota updates, quota failures, replication config updates, encryption and owner preservation, link-bucket rejection, layout preservation, and preExecute mutation.

`createSetBucketPropertyRequest` builds `SetBucketPropertyRequest` with `BucketArgs` containing bucket, volume, quota bytes, namespace quota, and versioning. The test suite uses `OmBucketArgs`, `OmBucketInfo`, `BucketEncryptionKeyInfo`, `DefaultReplicationConfig`, `ECReplicationConfig`, `CacheKey`, `CacheValue`, and `LogCapturer`.

Control flow starts by preExecuting to advance modification time and add user info. Success cases seed volume/bucket rows, validate updates, and inspect persisted bucket fields. Failure cases validate missing bucket, quota above volume quota, quota below current used bytes or namespace, and property update on a link bucket. Replication/encryption cases set EC replication while preserving existing quota or encryption key metadata.

State behavior is partial update of existing `bucketTable` rows. The tests assert FSO layout is preserved, encryption key and owner survive quota/replication changes, quota values are written, current usage blocks invalid lower quotas, and default replication config is either added or retained. Dependencies include OM quota semantics, link bucket metadata, protobuf bucket args, and logging.

Risks are loss of unrelated bucket fields during property update, quota accounting errors, link bucket mutation, and layout reset. Signals include `Status.OK`, `BUCKET_NOT_FOUND`, `QUOTA_EXCEEDED`, `QUOTA_ERROR`, `NOT_SUPPORTED_OPERATION`, persisted EC replication, retained encryption/owner, and expected error message/log content.

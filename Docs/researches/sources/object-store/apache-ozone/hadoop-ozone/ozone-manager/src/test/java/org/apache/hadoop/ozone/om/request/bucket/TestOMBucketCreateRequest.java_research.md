# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequest.java

Tests `OMBucketCreateRequest` for normal creation, preExecute mutation, strict S3 naming, bucket-count limits, ACL authorization failure, replication validation, quota enforcement, layout-specific name policy, and client ACL filtering.

Important helpers are `doPreExecute`, `doValidateAndUpdateCache`, `verifyRequest`, `verifySuccessCreateBucketResponse`, and `addCreateVolumeToTable`. `doPreExecute` seeds the volume table, builds a `CreateBucketRequest`, calls preExecute, and checks fields are preserved while creation time changes. `doValidateAndUpdateCache` sets UGI, calls validateAndUpdateCache, and compares the persisted `OmBucketInfo` to protobuf-derived expectations. The class uses `OmBucketInfo`, `OmVolumeArgs`, `DefaultReplicationConfig`, `ECReplicationConfig`, `BucketLayout`, `OzoneAcl`, and `OMException`.

Successful control flow is volume seed -> preExecute -> validateAndUpdateCache -> bucket table row. Failure paths omit the volume, create a duplicate bucket, exceed `OZONE_OM_MAX_BUCKET`, throw `PERMISSION_DENIED` from overridden `checkAcls`, supply invalid EC replication, exceed volume quota, create no-quota bucket under quota volume, or request invalid bucket names. Object-store buckets reject non-S3 names even with strict namespace disabled, while explicit FSO helper accepts them.

Persistence behavior centers on `bucketTable` keyed by `getBucketKey(volume, bucket)`. Tests assert creation/modification time, ACLs, version flag, storage type, metadata, and encryption info. Quota tests seed `volumeTable`; ignore-client-ACL tests verify requested ACLs are dropped or retained based on `OmConfig`.

Risks are policy interactions: strict S3 versus layout, quota rules, default replication validation, ACL bypass, and bucket count limits. Signals include `Status.OK`, `VOLUME_NOT_FOUND`, `BUCKET_ALREADY_EXISTS`, `QUOTA_EXCEEDED`, `QUOTA_ERROR`, `INVALID_REQUEST`, `PERMISSION_DENIED`, and `INVALID_BUCKET_NAME`.

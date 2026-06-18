# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/bucket/TestOMBucketCreateRequestWithFSO.java

FSO specialization of bucket create tests. It verifies `FILE_SYSTEM_OPTIMIZED` bucket layout when specified by CLI metadata and when sourced from OM default configuration, validates FSO create metrics, and confirms non-S3 bucket names are allowed for FSO when strict S3 namespace validation is disabled.

`setupWithFSO` sets `OZONE_DEFAULT_BUCKET_LAYOUT` to `OZONE_BUCKET_LAYOUT_FILE_SYSTEM_OPTIMIZED`. `doPreExecute` optionally adds `BucketLayoutProto.FILE_SYSTEM_OPTIMIZED` plus `OMRequestTestUtils.fsoMetadata`, preExecutes, and returns a request from the modified protobuf. The overridden `doValidateAndUpdateCache` constructs expected `OmBucketInfo` using the configured bucket layout and verifies persisted layout, metadata, ACLs, storage type, version flag, timestamps, and encryption key info.

State behavior is a successful `bucketTable` insert with `BucketLayout.FILE_SYSTEM_OPTIMIZED`; `omMetrics.getNumFSOBucketCreates` increments from 0 to 1. Integration points are superclass bucket create helpers, OM config keys, `getOMDefaultBucketLayout`, FSO metadata, and `UserGroupInformation`.

Risks are divergence between configured default layout and persisted layout, and accidental object-store-style name validation for FSO buckets. Test signals are `Status.OK`, non-null FSO bucket row, persisted FSO layout, and FSO metric increment.

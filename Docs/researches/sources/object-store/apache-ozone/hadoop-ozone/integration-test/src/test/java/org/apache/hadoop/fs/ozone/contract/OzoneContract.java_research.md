# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/contract/OzoneContract.java

Purpose: concrete Hadoop filesystem contract implementation for O3FS.

Important APIs/types/functions: final class extends `AbstractOzoneContract`; `getScheme` returns `o3fs`; `getTestPath` returns `/test`; `getRootURI` creates a volume and bucket using the configured default bucket layout and returns `o3fs://bucket.volume/`.

Control flow: when a contract test requests the test filesystem, the base class calls `getRootURI`; this class opens an `OzoneClient`, creates a fresh volume/bucket, formats the O3FS URI, and closes the client.

State and persistence behavior: each root URI creation persists a test volume and bucket in the mini cluster. The bucket layout follows `ozone.default.bucket.layout` from the contract configuration, defaulting to `BucketLayout.DEFAULT`.

Dependencies and integration points: uses `TestDataUtil.createVolumeAndBucket`, `OzoneClient`, `OzoneBucket`, `OzoneConsts.OZONE_URI_SCHEME`, and `OZONE_DEFAULT_BUCKET_LAYOUT`.

Risks: root URI creation has side effects and can leave buckets if contract cleanup misses them. Layout-dependent contract behavior is controlled externally by config.

Test signals: enables the abstract contract suite to validate O3FS semantics for the configured bucket layout.

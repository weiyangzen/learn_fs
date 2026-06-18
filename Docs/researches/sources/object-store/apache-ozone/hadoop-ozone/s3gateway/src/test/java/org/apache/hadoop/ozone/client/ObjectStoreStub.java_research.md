
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/client/ObjectStoreStub.java

Purpose: in-memory `ObjectStore` implementation for tests.

Important APIs and control flow: maintains a map of volume name to `OzoneVolumeStub`. `createVolume` constructs stub volumes from `VolumeArgs`. `getVolume` throws `VOLUME_NOT_FOUND` when absent. Volume listing filters by prefix and optional previous-volume marker, with one by-user method filtering owner. `getS3Volume` returns the configured default S3 volume. `createS3Bucket` lazily creates the S3 volume before creating a bucket; `deleteS3Bucket` delegates bucket deletion.

State, dependencies, integration: persistent test state is the in-memory `HashMap`. Default S3 volume name comes from `HddsClientUtils.getDefaultS3VolumeName(conf)`. Used by `OzoneClientStub`, `ClientProtocolStub`, and endpoint tests.

Risks and test signals: state is not thread-safe. Listing by user uses `< 0` for `prevVolume`, unlike normal forward pagination; if relied on, this may diverge from production. It does not support multitenant S3 volume behavior. Bucket endpoint tests rely heavily on create/get/delete S3 bucket behavior.

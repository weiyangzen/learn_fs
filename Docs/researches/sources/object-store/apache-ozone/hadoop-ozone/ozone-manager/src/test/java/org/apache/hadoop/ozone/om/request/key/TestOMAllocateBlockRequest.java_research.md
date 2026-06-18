# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/key/TestOMAllocateBlockRequest.java

Tests default-layout `OMAllocateBlockRequest` for preExecute block allocation, successful open-key update, and failure statuses when volume, bucket, or open key are missing.

The class extends `TestOMKeyRequest`. Helpers include `createAllocateBlockRequest`, `doPreExecute`, `getOmAllocateBlockRequest`, and `addKeyToOpenKeyTable`. PreExecute verifies command/client ID preservation, positive modification time, key location, expected container/local IDs, and pipeline presence. The success path seeds volume/bucket and open key rows, confirms the open key has no locations, validates the request, and re-reads the open key to confirm one appended block and updated modification time.

State behavior is mutation of an existing open key table row: latest version locations gain one `OmKeyLocationInfo`, creation time remains less than or equal to modification time, and block IDs match the preExecuted protobuf. Missing volume, bucket, or key states return failure statuses without creating the row. Dependencies are inherited SCM allocation mocks, OM metadata open key table, replication config, `OMRequestTestUtils`, and protobuf key location structures.

Risks are appending to the wrong open key, losing timestamps, or returning incorrect statuses for absent metadata. Signals are preExecute key location fields, `Status.OK`, open key location count 0 -> 1, matching block IDs, `VOLUME_NOT_FOUND`, `BUCKET_NOT_FOUND`, and `KEY_NOT_FOUND`.

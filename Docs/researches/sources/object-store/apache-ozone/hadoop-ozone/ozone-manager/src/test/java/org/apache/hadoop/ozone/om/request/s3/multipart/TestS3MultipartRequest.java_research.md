# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/multipart/TestS3MultipartRequest.java

Purpose: shared base fixture for S3 multipart request unit tests. It builds a mocked `OzoneManager` with real `OmMetadataManagerImpl`, metrics, audit logger, bucket-link resolution, and helper methods for pre-executing initiate, commit-part, abort, and complete MPU requests.

Important APIs and types: `OzoneManager`, `OMMetadataManager`, `OmMetadataManagerImpl`, `OMMetrics`, `AuditLogger`, `OzoneNativeAuthorizer`, `ResolvedBucket`, `OMLayoutVersionManager`, `OMRequestTestUtils`, `KeyValueUtil`, `S3InitiateMultipartUploadRequest`, `S3MultipartUploadCommitPartRequest`, `S3MultipartUploadAbortRequest`, and `S3MultipartUploadCompleteRequest`.

Control flow: `setup` configures a temp OM DB directory, constructs metadata manager and metrics, stubs `getOmMetadataReader`, access authorizer, audit logger, default replication config, bucket-link resolver, layout version manager, and OM config. `stop` unregisters metrics and clears inline mocks. Helper methods create protobuf requests, invoke request-specific `preExecute`, and assert expected mutation such as user info, multipart upload ID, modification time, metadata, and tags.

State and persistence behavior: no domain test state is asserted directly here, but the fixture defines all later tests' table environment. The real metadata manager means helper-created volumes, buckets, keys, open keys, multipart info, deleted table entries, and directory rows behave like OM tables rather than pure mocks.

Dependencies and integration points: request factory methods centralize request subclass selection. Subclasses override methods for FSO variants while reusing higher-level test flows. Bucket-link resolution always maps source and resolved volume/bucket to the same names with DEFAULT layout unless subclass-specific request constructors drive FSO behavior.

Risks covered: base helper assertions catch missing pre-execute mutations early. A misconfigured mock could invalidate many multipart tests, especially audit logging, authorizer state, and layout-version gates.

Test signals: pre-execute assertions on changed `OMRequest`, `hasInitiateMultiPartUploadRequest`, non-empty upload ID, positive modification time, and metadata/tag preservation; cleanup clears metrics/mocks between tests.

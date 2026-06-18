# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerListPartsAcls.java

Purpose: Unit tests ACL enforcement and metrics around `OzoneManager.listParts` for multipart upload part listing.

Important APIs and types: `OzoneManager.listParts`, `OmMetadataReader.checkAcls`, `KeyManager.listParts`, `OMMetrics`, `ResolvedBucket`, S3 authentication context, `OzoneObj.ResourceType.BUCKET`, `OzoneObj.ResourceType.KEY`, ACL `READ`, and `OmMultipartUploadListParts`.

Control flow: setup mirrors the multipart-upload listing ACL test: a real OM is spied, metadata reader/key manager/metrics are mocked, bucket links resolve requested to real names, and audit messages are mocked. Tests cover ACL-disabled path, ACL-enabled bucket-read then key-read order, bucket-read denial, and key-read denial.

State and persistence: no real metadata rows are needed. State is mock/spy side effects and per-test S3 auth cleared in `AfterEach`.

Dependencies and integration points: validates that object-level part listing checks both bucket and key READ ACLs after bucket-link resolution, delegates to key manager only after both pass, and records metrics/audit failures.

Risks and edge cases: failing bucket READ must skip key READ; failing key READ must skip key manager; success and failure metrics are distinct; audit failure construction should happen on denied requests.

Test signals: ordered ACL verifications, exact key-manager arguments, success/failure metric calls, `OMException` propagation, and absence of downstream calls after ACL denial.

# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/request/s3/tenant/TestSetRangerServiceVersionRequest.java

Purpose: tests `OMSetRangerServiceVersionRequest`, the OM request that records the Ranger service version synchronized to OM.

Important APIs and types: `OMSetRangerServiceVersionRequest`, `OMSetRangerServiceVersionResponse`, protobuf `SetRangerServiceVersionRequest`, `Type.SetRangerServiceVersion`, `OMPerformanceMetrics`, `OMLayoutVersionManager`, and `OmMetadataManagerImpl`.

Control flow: setup creates a mocked `OzoneManager`, layout version manager, real metadata manager, and mocked performance metrics. The test builds an OM request with Ranger service version `10L`, wraps it through `preExecute`, calls `validateAndUpdateCache` with transaction index `1`, casts the response, and reads the new service version string.

State and persistence behavior: the test validates response-level cache/update behavior by checking `getNewServiceVersion`; it does not inspect a DB table directly or batch-commit a response. The request is expected to store or expose the service version for later persistence by the response path.

Dependencies and integration points: integrates with OM metadata manager and performance metrics. It is part of the S3 tenant package because Ranger service version relates to tenant/Ranger synchronization.

Risks covered: request not preserving the provided long version, response class mismatch, and layout/metadata setup regressions causing validation failure.

Test signals: response is an `OMSetRangerServiceVersionResponse` and `Long.parseLong(getNewServiceVersion()) == 10L`.

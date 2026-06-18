# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisRequest.java

Purpose: focused tests for OM Ratis request conversion and unknown command handling.

Important APIs/types: `OzoneManagerRatisUtils.createClientRequest`, `OzoneManagerProtocolServerSideTranslatorPB`, `OMExecutionFlow`, `OMMetadataManager`, `OmMetadataManagerImpl`, `OMRequestTestUtils.createCompleteMPURequest`, `OMException`, `ProtocolMessageMetrics`, and `OzoneManagerProtocolProtos.Type.UnknownCommand`.

Control flow: `testRequestWithNonExistentBucket` creates a real metadata manager, inserts a volume only into the volume table cache, builds a Complete MPU request for a missing bucket, and asserts the Ratis utility raises `OMException.ResultCodes.BUCKET_NOT_FOUND`. `testUnknownRequestHandling` builds an `UnknownCommand` request, wires mocked OM execution flow/config, invokes the server-side translator, and compares the exact invalid-request response.

State and persistence behavior: temporary metadata state includes a cached volume entry and no bucket. No DB mutation is expected beyond setup. Unknown command processing returns an error response without writing metadata.

Dependencies and integration points: covers the boundary between protobuf OM requests, request factory creation, Ratis server-side translator, and OM execution flow.

Risks: the missing-bucket test depends on cache-visible volume state rather than a persisted volume row. Exact response equality can be brittle if error message wording changes.

Test signals: verifies semantic validation in request factory paths and graceful `INVALID_REQUEST` response for unrecognized write command types.

# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/TestCleanupTableInfo.java

## Purpose
This class validates `CleanupTableInfo` annotation coverage for concrete `OMClientResponse` subclasses and verifies selected create requests mark all touched metadata table caches for eviction. It is a response-layer integrity test rather than a single request test.

## Important APIs and Types
Key types include `CleanupTableInfo`, `OMClientResponse`, `OMFileCreateRequest`, `OMKeyCreateRequest`, `OMFileCreateResponse`, `OMKeyCreateResponse`, `OMEchoRPCWriteResponse`, `DummyOMClientResponse`, `OMMetadataManager`, `OmMetadataManagerImpl`, `OzoneManager`, `OMMetrics`, `OMPerformanceMetrics`, `OzoneLockProvider`, protobuf `CreateFileRequest`, `CreateKeyRequest`, `KeyArgs`, `KeyLocation`, and HDDS `Pipeline`.

## Control Flow and State
`setupOzoneManagerMock` creates a spy metadata manager in a temp directory, stubs OM metrics, metadata manager, audit logger, default replication config, and seeds volume and bucket rows with cache entries. `checkAnnotationAndTableName` scans `org.apache.hadoop.ozone.om.response` for all `OMClientResponse` subtypes, excludes echo and dummy responses, then asserts abstract classes lack cleanup annotations while concrete classes have them. It also verifies every named cleanup table exists in the metadata manager, or the annotation declares `cleanupAll`.

`testFileCreateRequestSetsAllTouchedTableCachesForEviction` and `testKeyCreateRequestSetsAllTouchedTableCachesForEviction` record cache item counts for every table, run request validation, and assert tables not named in the response annotation did not gain cache entries. The key-create path stubs filesystem paths, lock provider, and performance metrics. Helper methods build realistic file/key protobufs with three key locations and a pipeline.

## Dependencies and Integration Points
The test integrates reflection scanning, annotation metadata, metadata manager table lists, cache iterators, create request validation, metrics increments, lock provider setup, and protobuf block-location construction.

## Risks and Test Signals
Risks include new response classes missing cleanup annotations, annotations naming nonexistent tables, or request paths touching tables not listed for cleanup. Reflection assertions, cache-count comparisons, and metric verifications provide broad response-layer signals.

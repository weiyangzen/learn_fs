# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithOMResponse.java

Purpose: exercises `OzoneManagerDoubleBuffer` with actual OM request and response classes for volume and bucket create/delete workflows, including concurrent producers.

Important APIs/types: `OzoneManagerDoubleBuffer`, `OMVolumeCreateRequest/Response`, `OMBucketCreateRequest/Response`, `OMBucketDeleteRequest/Response`, `ExecutionContext`, `TermIndex`, `OMRequestTestUtils`, `OmMetadataManagerImpl`, volume and bucket tables, and `TransactionInfo`.

Control flow: setup builds mocked `OzoneManager`, real metadata manager, metrics, audit logger, and a large-capacity double buffer. Simple tests call `testDoubleBuffer` with increasing volume/bucket counts, spawning one daemon per volume. Mixed transaction tests create a volume, alternate bucket creates with deletes, wait for expected flushed count, then verify table row counts and row contents. Parallel mixed test runs two volume workflows concurrently and relaxes last-applied-index equality because transaction ordering can vary between threads.

State and persistence behavior: real metadata DB tables are updated by response batch operations. Cache validation runs through real request `validateAndUpdateCache` paths. The transaction info table is checked for exact term/index in serial mixed workflow and bounded index in parallel workflow.

Dependencies and integration points: integrates request validation, cache update, double-buffer persistence, audit logging, OM config, user identity, and table row counting.

Risks: high-count test (`MAX_VOLUMES` and 500 buckets each) can be expensive. Parallel test intentionally does not assert exact last-applied index. Empty catch around `setUGI` in `createBucket` can hide setup failure.

Test signals: proves real OM responses survive double-buffer batching, resulting DB rows match response payloads, deleted buckets are absent, and flush counts converge.

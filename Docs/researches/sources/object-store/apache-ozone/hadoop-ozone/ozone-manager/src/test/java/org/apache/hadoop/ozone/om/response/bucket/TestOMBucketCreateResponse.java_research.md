# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketCreateResponse.java

Purpose: Verifies `OMBucketCreateResponse.addToDBBatch` writes a new bucket entry to OM metadata.

Important APIs/types/functions: Uses `OmMetadataManagerImpl`, `BatchOperation`, `Table.KeyValue`, `OMBucketCreateResponse`, protobuf `CreateBucketResponse`, `OMResponse`, and `TestOMResponseUtils.createBucket`.

Control flow: The test creates a temp OM DB, opens one batch, builds random volume/bucket names and an `OmBucketInfo`, confirms `bucketTable` is empty, constructs a successful `CreateBucket` OM response wrapper, adds it to the batch, commits manually, then iterates the table.

State/persistence: Persists one row in `bucketTable` under `omMetadataManager.getBucketKey(volume,bucket)` with the exact `OmBucketInfo` value supplied to the response.

Dependencies/integration: Exercises the response class against the real metadata store abstraction and batch-commit path rather than mocking table writes.

Risks/test signals: It covers only the success path and assumes iterator order with a single row. Regression signal is table row count one plus exact key/value equality after batch commit.

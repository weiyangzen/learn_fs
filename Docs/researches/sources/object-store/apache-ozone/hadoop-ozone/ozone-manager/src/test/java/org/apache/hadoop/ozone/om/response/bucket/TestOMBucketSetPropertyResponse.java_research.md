# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/response/bucket/TestOMBucketSetPropertyResponse.java

Purpose: Verifies `OMBucketSetPropertyResponse` writes updated bucket properties to `bucketTable`.

Important APIs/types/functions: Uses `OMBucketSetPropertyResponse`, `OmBucketInfo`, protobuf `CreateBucketResponse`/`OMResponse`, `BatchOperation`, and `Table.KeyValue`.

Control flow: The test creates random volume/bucket names and an `OmBucketInfo`, wraps it in a successful response, calls `addToDBBatch`, commits, counts the bucket table, and checks the single key/value.

State/persistence: Persists exactly one bucket row under the canonical bucket DB key with the supplied bucket info. It does not pre-create a previous bucket version, so this behaves as an upsert check.

Dependencies/integration: Covers real metadata-store batch writing for bucket property updates.

Risks/test signals: The command type is `CreateBucket` even though the response type is set-property; this test focuses on DB mutation, not protobuf semantic fidelity. It does not compare before/after property deltas.

# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerDoubleBufferWithDummyResponse.java

Purpose: validates `OzoneManagerDoubleBuffer` with a simple custom `OMClientResponse` that writes bucket rows, proving flush-to-DB and transaction info persistence without full OM request handling.

Important APIs/types: `OzoneManagerDoubleBuffer`, `OzoneManagerDoubleBufferMetrics`, `OMMetadataManager`, `OmMetadataManagerImpl`, `TransactionInfo`, `TermIndex`, `OMClientResponse`, `@CleanupTableInfo(cleanupTables = {BUCKET_TABLE})`, and nested `OMDummyCreateBucketResponse`.

Control flow: setup creates a temporary metadata DB and starts the double buffer. The test asserts zero initial metrics, adds 100 dummy bucket create responses with monotonically increasing `TermIndex`, waits until flushed transaction count reaches 100, then validates metrics, bucket table row count, singleton metrics object identity, and `TRANSACTION_INFO_KEY` term/index persistence.

State and persistence behavior: real RocksDB-backed OM metadata tables are mutated. Each dummy response writes an `OmBucketInfo` into the bucket table through a batch operation. The double buffer persists the last applied transaction info with term `1` and index equal to the bucket count.

Dependencies and integration points: integrates batch write behavior, cleanup table annotations, bucket table definitions, metrics, and async double-buffer daemon flushing. Uses `GenericTestUtils.waitFor` to observe eventual flush.

Risks: depends on async timing with a 60-second bound. The dummy response covers bucket table writes but not validation/cache preconditions from real OM requests.

Test signals: confirms flush operation count, max/avg transactions per flush, queue size metrics, bucket table persistence, flush iteration count, and transaction info persistence.

# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmMetrics.java

## Purpose
Integration test suite for `OMMetrics` counters across volume, bucket, key, directory, snapshot, and ACL operations. It validates both success counters and failure counters by combining real MiniOzoneCluster operations with white-box fault injection.

## Important APIs, types, and functions
- Uses `MiniOzoneCluster`, `OzoneManagerProtocol`, `ObjectStore`, `OMMetrics`, `MetricsAsserts.getMetrics/getLongCounter`, and `HddsWhiteboxTestUtils`.
- Operation helpers `doVolumeOps`, `doBucketOps`, and `doKeyOps` intentionally swallow IO exceptions so metric increments can be asserted after injected failures.
- `mockWritePathExceptions` spies `OMMetadataManager` tables and forces `RocksDatabaseException` from `Table.isExist` to exercise write failure metrics.
- Key helpers build `OmKeyArgs` with `OmKeyLocationInfo`, `BlockID`, `MockPipeline`, Ratis or EC replication configs, and owner names.

## Control flow
The suite starts a five-datanode cluster with metrics-save interval, faster directory deleting service, filesystem-path support, and snapshot rename enabled. Each operation test records initial counters, performs successful operations, verifies deltas, injects manager or metadata failures, repeats operations, verifies failure deltas, and restores white-box state. Snapshot testing creates keys and snapshots, waits for diff jobs, lists/cancels diffs, gets/lists/renames/deletes snapshots, and checks invalid cases. Directory testing runs for `FILE_SYSTEM_OPTIMIZED` and `LEGACY` bucket layouts through OFS filesystem paths.

## State and persistence behavior
The test creates real OM metadata in RocksDB through cluster APIs. It observes aggregate counters such as current `NumVolumes`, `NumBuckets`, `NumKeys`, active/deleted snapshot counts, EC bucket/key create totals, block allocation failures, and directory delete cleanup effects. Background services matter: directory deletion must decrement key counts, and snapshot diff jobs must reach `DONE`.

## Dependencies and integration points
It integrates OM manager classes (`VolumeManager`, `BucketManager`, `KeyManager`, `OmMetadataReader`), Ozone client protocol, Hadoop `FileSystem` over OFS, snapshot diff service, ACL authorization types, metrics2/JMX records, EC replication placement, and RocksDB table abstractions.

## Risks and edge cases
The test is timing-sensitive around background directory deletion and snapshot diff completion. It also relies on private-field names for white-box replacement, so refactors of OM internals can break tests without changing external behavior. Counter deltas are exact and may need updates when new sub-operations are added.

## Test signals
Signals are exact metric counter deltas after success and failure paths, expected EC placement failure text for insufficient datanodes, `GenericTestUtils.waitFor` cleanup convergence, snapshot invalid-operation exceptions, and direct `OMMetrics` getter increments for HA-style ACL calls.

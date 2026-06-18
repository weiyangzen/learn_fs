# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneDebugShell.java

## Purpose
`TestOzoneDebugShell` validates broader `ozone debug` commands for replica verification, chunk-info output, unique DN block-file paths, and `ldb` scanning of snapshot checkpoint RocksDB databases.

## Important APIs, Types, and Functions
The abstract non-HA test uses `OzoneDebug`, `RDBParser`, `OMMetadataManager`, `TestDataUtil.createVolumeAndBucket/createKey`, RATIS and EC replication configs, `OzoneTestUtils.closeContainer`, OM key lookup through `OmKeyArgs`, and Jackson `ObjectMapper` to parse chunk-info JSON. It parameterizes over EC vs RATIS keys and all `BucketLayout` enum values.

## Control Flow, State, and Persistence
Each test creates a fresh client and debug shell. `testReplicasVerifyCmd` writes a key and runs `replicas verify --checksums --block-existence --container-state`. `testChunkInfoCmdBeforeAfterCloseContainer` runs chunk-info before and after closing the key's container. `testChunkInfoVerifyPathsAreDifferent` parses chunk-info JSON and asserts three distinct block file paths, matching three datanode storage directories. `testLdbCliForOzoneSnapshot` creates a snapshot, constructs the snapshot DB path from the checkpoint directory, waits for `CURRENT`, scans the key table column family via `RDBParser`, and verifies the key name appears.

## Dependencies and Integration Points
This integrates debug CLI commands, OM/SCM address injection, replica verification checks, chunk file path reporting, container close behavior, snapshot checkpoint persistence, RocksDB column-family scanning, and multiple bucket layouts/replication types.

## Risks and Test Signals
Risks include JSON output schema drift, snapshot DB path construction depending on OM storage layout, and asynchronous checkpoint creation. Signals are zero command exit codes, distinct per-DN file paths, and visible snapshot key entries in ldb scan output.

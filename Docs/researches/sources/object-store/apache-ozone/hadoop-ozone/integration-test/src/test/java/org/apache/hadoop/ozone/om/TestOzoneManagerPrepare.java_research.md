# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOzoneManagerPrepare.java

## Purpose
Integration coverage for HA Ozone Manager prepare/cancel behavior against a real `MiniOzoneHAClusterImpl`. The test verifies that preparing an OM Ratis group blocks mutating OM requests, preserves already committed metadata, purges Ratis log files, survives restarts, and allows lagging peers to catch up to the prepare transaction.

## Important APIs and Types
Primary test type: `TestOzoneManagerPrepare`, extending `TestOzoneManagerHA`. Important helpers include `submitPrepareRequest`, `submitCancelPrepareRequest`, `assertClusterPrepared`, `assertClusterNotPrepared`, `assertRatisLogsCleared`, `writeKeysAndWaitForLogs`, `assertKeysWritten`, and `logFilesPresentInRatisPeer`. It uses `ClientProtocol`, `OzoneManagerPrepareState.State`, `PrepareStatus`, `OMMetadataManager`, `OmKeyInfo`, `MiniOzoneHAClusterImpl`, Ratis `RaftServer.Division`, and `OMException.ResultCodes.NOT_SUPPORTED_OPERATION_WHEN_PREPARED`.

## Control Flow
`@BeforeEach` waits for an OM leader, cancels any inherited prepare state, and asserts the cluster is writable. Test methods then issue writes, shutdown/restart OMs, submit prepare through `clientProtocol.getOzoneManagerClient().prepareOzoneManager`, and poll every OM until its prepare status reaches `PREPARE_COMPLETED` at or beyond the returned log index. Read requests are expected to continue, while write requests are expected to fail once prepared. `testPrepareWithMultipleThreads` races one prepare request against volume creation tasks and accepts either successful pre-prepare writes or explicit prepared-state failures.

## State and Persistence
The important persistent state is OM metadata in RocksDB and OM Ratis logs on disk. `writeKeysAndWaitForLogs` forces data writes and waits until each target OM has Ratis log files, making later log purge assertions meaningful. `assertKeysWritten` reads each OM's local metadata manager rather than only the client-visible majority, so it detects follower data loss. Prepare state must persist through full OM restart and be catch-up replicated to a previously downed OM.

## Dependencies and Integration Points
The test couples OM client RPC, HA Ratis replication, OM prepare state, metadata tables, mini-cluster lifecycle, and filesystem-level Ratis storage directories. It also uses `TestDataUtil` and `ContainerTestHelper` to create object-store keys.

## Risks and Edge Cases
The test is marked flaky for HDDS-5990 and one downed-OM case is unhealthy pending Ratis behavior. Assertions depend on log file naming and storage layout under Ratis directories. Timing is intentionally long because lagging followers and log purge are asynchronous. Concurrent prepare/write outcomes are nondeterministic but constrained by result code checks.

## Test Signals
Strong signals include prepare index propagation to all OMs, Ratis logs disappearing after prepare, reads succeeding while writes fail in prepared state, cancel restoring writes, two-down-OM quorum failure, one-down-OM catch-up, prepare persistence across restart, and repeated prepare idempotence.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestValidateBCSIDOnRestart.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestValidateBCSIDOnRestart.java

Purpose: This test validates datanode restart behavior when container block-commit sequence ID state is missing or inconsistent. It protects container state-machine recovery and corruption detection around BCSID.

Important APIs/types/functions: Setup disables stream flush delay, shortens heartbeat/report/stale/destroy intervals, configures RATIS client/server timeouts, starts a 2-datanode cluster, and waits for a RATIS/ONE pipeline. The test uses `OzoneOutputStream`, `KeyOutputStream`, `OmKeyLocationInfo`, `TestHelper.getDatanodeService`, `OzoneContainer`, `ContainerStateMachine`, `SimpleStateMachineStorage`, `StatemachineImplTestUtil.findLatestSnapshot`, `HddsDispatcher.getMissingContainerSet`, `BlockUtils.getDB`, and `KeyValueContainerData.getBcsIdKey`.

Control flow: The test writes and flushes a key to create a container, captures the datanode and container data, closes the key, deletes the container path, removes the container from the in-memory container set, takes a state-machine snapshot, and calls `buildMissingContainerSet`. It asserts the latest snapshot exists and the dispatcher missing-container set contains the deleted container ID. It then writes another key, locates its container, opens the container DB, corrupts the stored BCSID by writing `0L`, restarts the datanode, and asserts the container state becomes `UNHEALTHY`.

State and persistence behavior: It deliberately mutates on-disk container directories and RocksDB metadata. It validates snapshot-derived missing-container state and restart-time comparison between container file state and DB BCSID.

Dependencies and integration points: Covers datanode container set rebuild, RATIS state machine snapshots, dispatcher missing-container tracking, KeyValueContainer metadata, DB handle access, and datanode restart.

Risks: This is invasive: it deletes container files and corrupts RocksDB inside a live test cluster. Timing of snapshots and container reports must match the shortened intervals.

Test signals: Passing means missing containers are discovered from snapshots and BCSID mismatches are detected by marking containers unhealthy after restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestValidateBCSIDOnRestart.java -->

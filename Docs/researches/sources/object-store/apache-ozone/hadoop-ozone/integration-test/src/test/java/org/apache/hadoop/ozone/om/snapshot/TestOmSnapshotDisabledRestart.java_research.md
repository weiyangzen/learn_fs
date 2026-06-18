# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOmSnapshotDisabledRestart.java

Purpose: This unhealthy-marked integration test verifies startup protection when snapshot support is disabled after snapshots already exist. It asserts that an OM refuses to restart with the feature disabled while snapshot metadata remains.

Important APIs/types/functions: The class uses `MiniOzoneHAClusterImpl`, `ObjectStore`, `OzoneVolume`, `OZONE_FILESYSTEM_SNAPSHOT_ENABLED_KEY`, `cluster.shutdownOzoneManager`, `cluster.restartOzoneManager`, and AssertJ/JUnit assertions. The test is tagged `@Unhealthy("HDDS-8945")`.

Control flow: Setup enables snapshots and starts a three-node HA OM cluster. The test creates a volume, bucket, and snapshot. It then iterates over every OM, shuts the OM down, flips that OM configuration to disable snapshots, asserts restart fails with a `RuntimeException` containing `snapshots remaining`, re-enables the feature, and restarts successfully.

State and persistence behavior: The persistent state under test is pre-existing snapshot metadata and checkpoint state in OM DB. The test ensures configuration downgrade does not silently strand snapshots or boot into a mode unable to manage them. It validates both failure and recovery startup paths for each OM process.

Dependencies and integration points: This test integrates OM startup validation with snapshot metadata discovery, HA node lifecycle management, per-OM runtime configuration mutation, and existing snapshot state produced through public `ObjectStore` APIs.

Risks and edge cases: The test mutates OM configuration while cycling all HA nodes, so it is sensitive to leader election and restart timing. The asserted message is substring-based, so a behavior-preserving wording change around startup failure can still matter. The unhealthy tag indicates known instability or tracked issue context.

Test signals: A correct implementation throws on restart with disabled snapshots and remaining snapshot state, includes `snapshots remaining` in the failure, and restarts cleanly after the feature is enabled again.

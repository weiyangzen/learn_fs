# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureToleration.java

Purpose: Integration test for startup-time datanode tolerance of failed data volumes. It verifies one failed volume is tolerated when configured, while a second failed volume triggers datanode shutdown.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `UniformDatanodesFactory` with three data volumes, `DatanodeConfiguration.setFailedDataVolumesTolerated`, `DatanodeTestUtils`, `ExitUtil`, `DatanodeStateMachine`, and log capture.

Control flow: Per-test setup builds a one-datanode cluster with three data volumes, replication one, fast heartbeat/report intervals, and tolerated failed data volumes set to one. The test marks the first volume root bad and restarts the datanode successfully. It then marks a second volume root bad, disables JVM exit, captures datanode and exit logs, restarts without waiting for full success, waits for `ExitException` logging, asserts datanode shutdown due to too many bad volumes, and restores both roots.

State and persistence behavior: Volume root permissions are changed to simulate startup failure. Restarting the datanode reloads volume health state. Exceeding tolerance invokes process-exit logic, intercepted by `ExitUtil.disableSystemExit`.

Dependencies and integration points: Covers volume initialization during datanode startup, failed-volume tolerance config, datanode state machine shutdown behavior, and process-exit handling.

Risks: Relies on filesystem permission changes and log messages. Because system exit is disabled, the failed datanode may not actually terminate exactly as production would. Timed wait allows up to 60 seconds for restart/shutdown logging.

Test signals: First restart with one bad volume must not throw. Second restart must log an exit with status 1 and `DatanodeStateMachine Shutdown due to too many bad volumes`.

# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestRefreshVolumeUsageHandler.java

Purpose: This integration test verifies the datanode and SCM path for refreshing volume usage information. It checks that SCM node usage eventually reflects data written on a datanode and that an explicit refresh-volume-usage command can force updated usage reporting.

Important APIs and types: The test uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneOutputStream`, `DatanodeDetails`, `ScmNodeManager.getUsageInfo`, `refreshAllHealthyDnUsageInfo`, `DUOptimized`, `HddsVolumeFactory`, `VolumeUsage.refreshNow`, and `GenericTestUtils.waitFor`.

Control flow: `setup` builds a one-datanode cluster with 1 GB containers, a 5 GB minimum datanode volume free-space setting, one-second node reports, the `HddsVolumeFactory` DU implementation, zero RATIS minimum free space, and safemode pipeline creation disabled. The test records the current SCM-used value, captures `DUOptimized` logs, writes a small key, first asserts SCM usage has not immediately changed, then waits for node reports to show a larger used value. It asks SCM node manager to refresh all healthy datanode usage info, waits again for updated usage, directly calls `refreshNow` on the datanode volume usage, and waits for the optimized DU log to mention container data usage.

State and persistence behavior: The durable state is actual key data written to the datanode volume. The observed state is SCM's cached node usage statistics and the datanode volume-usage cache. The explicit refresh path should cause SCM-visible used space to advance beyond the initial value without waiting for the default long DU refresh period.

Dependencies and integration points: Coverage includes client writes, datanode volume usage tracking, node reports, SCM node manager usage aggregation, refresh usage command scheduling, and optimized disk-usage accounting.

Risks: The test depends on filesystem usage changes being visible and on log text from `DUOptimized`. It tolerates one timeout during the pre-refresh wait because the node report might not refresh quickly, but the final assertions still depend on timing.

Test signals: Signals include initial equality of SCM used space, eventual `ScmUsed` greater than the recorded value, successful explicit refresh through `refreshAllHealthyDnUsageInfo`, and a `DUOptimized` log line containing the expected container data usage count after `refreshNow`.

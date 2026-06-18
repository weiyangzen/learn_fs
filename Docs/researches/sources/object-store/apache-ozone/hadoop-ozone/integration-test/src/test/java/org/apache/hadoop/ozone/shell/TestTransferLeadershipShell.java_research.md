# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestTransferLeadershipShell.java

Purpose: This HA integration suite validates OM and SCM leadership transfer commands. It tests explicit target transfer with `-n` and randomized transfer with `-r`, and verifies Ratis peer priorities are reset after transfer.

Important APIs and types: The file uses `MiniOzoneHAClusterImpl`, `MiniOzoneCluster.newHABuilder`, `OzoneAdmin`, `OzoneManager`, `StorageContainerManager`, `RatisHelper.NEUTRAL_PRIORITY`, `RaftPeer`, and `ScmConfigKeys.OZONE_SCM_HA_RATIS_SNAPSHOT_THRESHOLD`.

Control flow: `init` configures a low SCM HA Ratis snapshot threshold, builds a three-OM/three-SCM fully active HA cluster, and waits for readiness. `testOmTransfer` finds the OM leader, selects a follower, executes `om transfer -n`, sleeps, verifies the selected OM is leader, checks priorities, then executes `om transfer -r` and expects a different leader. `testScmTransfer` performs the same explicit and random flow for SCM using `scm transfer`.

State and persistence behavior: The tests mutate runtime Ratis leadership and peer priorities. No user object data is created. The snapshot threshold configuration affects SCM Ratis behavior during the cluster lifetime. Cluster shutdown is explicit in `@AfterAll`.

Dependencies and integration points: It integrates admin CLI commands with OM and SCM HA Ratis servers, leader election/transfer APIs, cluster leader-discovery helpers, and Ratis peer group priority metadata.

Risks: `Thread.sleep(3000)` for OM transfer is timing-sensitive; SCM uses `waitForClusterToBeReady`. Random transfer only asserts leader inequality and may be sensitive if transfer fails or leadership changes concurrently. Priority assertions assume all peers are visible from the new leader and should be neutral after command completion.

Test signals: Signals include equality with the requested new leader after explicit transfer, inequality after randomized transfer, non-null SCM leader lookup, and every OM/SCM Ratis peer priority equal to `NEUTRAL_PRIORITY`.

# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFollowerRead.java

Purpose: This subclass runs the shell HA suite with follower-read support enabled and adds targeted tests for leader skip-linearizable-read metrics and follower local-lease consistency. It verifies that shell read commands can exercise OM follower-read paths without breaking inherited shell behavior.

Important APIs and types: It uses `OzoneManagerRatisServerConfig`, `RaftServerConfigKeys.Read.Option.LINEARIZABLE`, `OzoneManager`, `OzoneShell`, and OM metrics such as `getNumLeaderSkipLinearizableRead`, `getNumFollowerReadLocalLeaseSuccess`, and `getNumFollowerReadLocalLeaseFailTime`.

Control flow: `init` configures linearizable reads, leader lease, leader skip optimization, client follower read, hsync, and HBase enhancements before starting the inherited HA cluster. `testAllowLeaderSkipLinearizableRead` repeatedly runs `volume list` with follower read enabled, observes the leader skip metric, disables skip on the leader, repeats reads, and verifies the metric stops increasing. `testAllowFollowerReadLocalLease` selects two non-leader OMs, configures one with valid local lease and one with negative lease time, runs repeated `volume list` commands with `LOCAL_LEASE`, then changes the second follower to unlimited lease/log lag and verifies success.

State and persistence behavior: The tests mutate live OM configurations and restore them in `finally` blocks. Persistent object-store state is not central; runtime state is OM Ratis read configuration and metrics counters accumulated by shell read requests.

Dependencies and integration points: The file integrates shell command execution, OM HA leader/follower roles, Ratis read options, follower-read client configuration, dynamic OM configuration updates, and OM metrics. It depends on a stable leader and at least two followers.

Risks: Metrics-based assertions require enough repeated reads to hit intended servers and can be sensitive to routing changes. Follower selection checks `!om.isLeaderReady()`, so leader transitions during the test could affect which OMs are configured. Config restoration is critical for inherited tests.

Test signals: Signals are a positive leader-skip metric before disabling the feature, unchanged leader-skip metric after disabling, local-lease success on a configured follower, local-lease failure-time increments on the follower with negative lease time, and later local-lease success after allowing infinite lag.

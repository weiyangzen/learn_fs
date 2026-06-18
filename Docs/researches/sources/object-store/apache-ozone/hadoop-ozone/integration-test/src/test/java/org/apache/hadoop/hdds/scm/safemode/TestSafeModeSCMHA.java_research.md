<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeSCMHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeSCMHA.java

Purpose: Tests that an SCM follower in an HA cluster can restart and exit safe mode after state has synced from the leader.

Important APIs and types: Uses `MiniOzoneHAClusterImpl`, HA builder with OM and SCM service IDs, `StorageContainerManager`, `SCMStateMachine`, `LastAppliedTermIndex`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, and `RatisReplicationConfig`.

Control flow: Setup builds an HA cluster with one OM and three SCMs, all active. The test creates a volume, bucket, and Ratis three key, identifies one leader SCM and one follower SCM, waits until leader and follower SCM state machines have the same applied log index, restarts the follower SCM, and waits until the restarted follower leaves safe mode.

State and persistence behavior: HA SCM Ratis log state must replicate the object/container changes to the follower before restart. On restart, follower safe-mode state is derived from replicated SCM metadata and live reports.

Dependencies and integration points: Covers SCM HA Ratis replication, follower restart, safe-mode exit, OM/object-store writes, and cluster HA service wiring.

Risks: The leader/follower selection keeps the last non-leader encountered as follower. Waiting for equal log index does not compare term or all internal state, but it is the synchronization signal used here. Safe-mode exit depends on datanode reports after follower restart.

Test signals: Signals include non-null leader and follower, equal last-applied indexes before restart, and restarted follower `isInSafeMode` becoming false.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSafeModeSCMHA.java -->

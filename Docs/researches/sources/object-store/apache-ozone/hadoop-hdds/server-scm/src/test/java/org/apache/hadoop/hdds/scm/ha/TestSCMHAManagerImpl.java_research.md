<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAManagerImpl.java

Purpose: This integration-heavy suite verifies `SCMHAManagerImpl` and `SCMRatisServerImpl` behavior for adding/removing SCM peers and rejecting invalid HA-ring removal requests.

Important APIs and types: It uses `SCMHAManagerImpl`, `SCMRatisServerImpl.initialize`, `SCMRatisServer`, `AddSCMRequest`, `RemoveSCMRequest`, `StorageContainerManager`, `SCMHANodeDetails`, `SCMNodeDetails`, `SCMSnapshotProvider`, `DivisionInfo`, `GenericTestUtils.waitFor`, and many mocked SCM subsystems.

Control flow: `BeforeAll` creates a leader SCM manager with local Ratis storage/metadata dirs, starts it, waits until its Ratis division is leader-ready, then creates a follower SCM manager. `testAddSCM` starts the follower and adds it to the leader's Ratis group, increasing peer count from one to two. `testRemoveSCM` removes the follower and expects peer count one. `testHARingRemovalErrors` creates an SCM via `HddsTestUtils.getScm` and verifies removing a non-peer or the current leader produces an IOException with identifying text.

State and persistence behavior: The test creates temporary Ratis and metadata directories for leader and follower. Runtime state includes live Ratis server peer membership and mocked SCM metadata/transaction components.

Dependencies and integration points: It stitches together HA manager startup, Ratis peer group mutation, snapshot-provider override, SCM service wiring, and StorageContainerManager HA ring API validation.

Risks: The ordered tests depend on prior peer count and live local Ratis servers. Port use is fixed for leader/follower mocks, so environment conflicts are possible.

Test signals: Ratis division leader readiness, peer count changes 1 -> 2 -> 1, follower start/stop, and expected errors for removing non-peer or leader SCM IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHAManagerImpl.java -->

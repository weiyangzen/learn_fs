<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisServerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisServerImpl.java

Purpose: This test verifies `SCMRatisServerImpl.getLeaderId` returns the current Ratis leader peer ID or null when no leader is known.

Important APIs and types: It uses `SCMRatisServerImpl`, mocked construction for `SecurityConfig`, static mocks for `RaftServer.newBuilder` and `RatisUtil.newRaftProperties`, mocked `RaftServer.Builder`, `RaftServer`, `RaftServer.Division`, `SCMStateMachine`, `RaftPeer`, and `RaftPeerId`.

Control flow: The test mocks enough construction plumbing to instantiate a spied `SCMRatisServerImpl` without a real Raft server. It stubs `getLeader` to return a `RaftPeer` with ID `peer1`, asserts `getLeaderId` returns that ID, then stubs `getLeader` to null and asserts `getLeaderId` returns null.

State and persistence behavior: No persistent state is created. Runtime state is fully mocked construction and spy behavior.

Dependencies and integration points: This isolates a small leader lookup contract used by SCM HA status, metrics, and request routing.

Risks: Heavy static/construction mocking means the test guards method behavior but not full server initialization.

Test signals: Exact `RaftPeerId.valueOf("peer1")` result and null result when leader is absent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisServerImpl.java -->

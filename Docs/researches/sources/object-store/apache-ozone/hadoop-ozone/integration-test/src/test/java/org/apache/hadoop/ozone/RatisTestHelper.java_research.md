# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/RatisTestHelper.java

Purpose: static helper interface for Ratis-related Ozone integration tests. It configures Ratis transport and exposes datanode raft server division/state-machine/role lookup for a pipeline.

Important APIs/types/functions: `initRatisConf`, `initXceiverServerRatis`, `getRaftServerDivision`, `getStateMachine`, `isRatisLeader`, and `isRatisFollower`. It uses `RatisHelper`, `XceiverServerRatis`, `RaftClient`, `RaftPeer`, `RaftServer.Division`, `StateMachine`, `RpcType`, and Ozone Ratis configuration keys.

Control flow: `initRatisConf` enables container Ratis, selects RPC type, shortens container report interval, and extends SCM stale node interval. `initXceiverServerRatis` converts a datanode to a raft peer, opens a short-lived Raft client, and adds a raft group for the pipeline. `getRaftServerDivision` first verifies the pipeline includes the datanode, casts the datanode write channel to `XceiverServerRatis`, and looks up the server division by raft group ID. Role/state-machine helpers delegate to that division.

State and persistence: mutates test configuration and raft group membership. Reads live raft server state from a datanode process.

Dependencies and integration points: HDDS Ratis helpers, datanode write channel, Ratis group management API, pipeline membership and raft group conversion.

Risks: assumes the DN write channel is Ratis-backed; callers must configure/start cluster accordingly. Throws `IllegalArgumentException` for non-member DNs. Role checks are instantaneous and may race with leader election.

Test signals: downstream tests can assert leader/follower role, inspect state machine, or initialize raft groups without duplicating Ratis boilerplate.

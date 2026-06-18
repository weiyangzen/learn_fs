# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithDatanodeFastRestart.java

Purpose: Freon integration test for datanode fast restart without waiting for pipeline closure, with Ratis snapshot verification. Marked unhealthy for HDDS-1160.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `RandomKeyGenerator`, `StateMachine`, `SimpleStateMachineStorage`, `SingleFileSnapshotInfo`, `TermIndex`, and `TestHelper.getStateMachine`. Helper `startFreon` runs one 20 MB Ratis THREE validated write.

Control flow: Setup starts a three-datanode mini cluster with one-second SCM heartbeat processing. The test runs Freon once, records the Ratis state machine last applied term/index, restarts datanode 0 without waiting, obtains the restarted state machine storage, verifies the latest snapshot file corresponds to the pre-restart term/index, checks post-restart term index is not behind, sleeps five seconds for datanode SCM registration, then runs Freon again.

State and persistence behavior: Freon writes replicated data and advances Ratis state. Datanode restart creates or exposes a snapshot in state machine storage. The test checks snapshot file path and term/index persistence across restart.

Dependencies and integration points: Exercises Freon writes, datanode restart behavior, Ratis state machine snapshotting, SCM heartbeat registration, and post-restart pipeline usability.

Risks: Explicit `Thread.sleep(5000)` documents a known race with SCM registration and possible `scmId cannot be null` crash. The test is marked unhealthy. Snapshot path expectations are tightly coupled to Ratis storage naming.

Test signals: Freon counters must show one volume/bucket/key and zero validation failures before and after restart; snapshot file and term index must match pre-restart last applied term/index; post-restart index must be greater than or equal to before.

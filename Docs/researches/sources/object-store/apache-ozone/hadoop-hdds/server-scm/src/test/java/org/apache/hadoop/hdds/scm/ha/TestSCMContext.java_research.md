<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMContext.java

Purpose: This compact test verifies `SCMContext` state transitions for Raft leadership and SCM safe mode.

Important APIs and types: It uses `SCMContext.Builder`, `updateLeaderAndTerm`, `setLeaderReady`, `getTermOfLeader`, `updateSafeModeStatus`, and `SafeModeStatus`.

Control flow: The Raft test starts as follower, updates to leader term 10, marks leader ready, then steps down and expects leader-ready to reset. The safe-mode test starts in `INITIAL`, moves to `PRE_CHECKS_PASSED`, then `OUT_OF_SAFE_MODE`, checking both `isInSafeMode` and `isPreCheckComplete`.

State and persistence behavior: State is in-memory context flags and term values. No persistence is involved.

Dependencies and integration points: `SCMContext` is consumed by background services, state machines, and HA role-aware managers to decide whether to run or pause.

Risks: Incorrect leader-ready or safe-mode transitions can cause services to run at the wrong time.

Test signals: Boolean leader, leader-ready, safe-mode, pre-check flags, and exact leader term.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMContext.java -->

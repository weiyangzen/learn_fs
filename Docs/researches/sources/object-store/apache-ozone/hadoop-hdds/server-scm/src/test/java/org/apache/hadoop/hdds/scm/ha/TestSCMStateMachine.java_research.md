<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMStateMachine.java

Purpose: This compact test verifies that `SCMStateMachine` records Ratis configuration-change events into SCM metrics.

Important APIs and types: It uses `SCMStateMachine`, `SCMMetrics`, mocked `StorageContainerManager`, mocked `SCMHADBTransactionBuffer`, `TransactionInfo`, `TermIndex`, and `RaftConfigurationProto`.

Control flow: The test creates SCM metrics, wires them into a mocked SCM, stubs the transaction buffer's latest transaction info, constructs an `SCMStateMachine`, calls `notifyConfigurationChanged`, and asserts the metrics event log contains the configuration-change text. Metrics are unregistered at the end.

State and persistence behavior: Runtime metrics state is mutated. No persistent DB is touched.

Dependencies and integration points: This guards observability for SCM HA/Ratis state-machine events.

Risks: Exact event text is a diagnostics contract. The test does not validate other state-machine callbacks.

Test signals: `metrics.getRatisEvents()` contains "Configuration changed at term index".
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMStateMachine.java -->

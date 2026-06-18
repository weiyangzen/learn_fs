<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestStatefulServiceStateManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestStatefulServiceStateManagerImpl.java

Purpose: This test verifies `StatefulServiceStateManagerImpl` can save and read service configuration through the SCM HA DB transaction buffer.

Important APIs and types: It uses `StatefulServiceStateManagerImpl.newBuilder`, `StatefulServiceStateManager`, `SCMDBDefinition.STATEFUL_SERVICE_CONFIG`, `DBStoreBuilder`, `SCMHAManagerStub`, `SCMHADBTransactionBuffer`, and protobuf `ByteString`.

Control flow: Setup opens a real SCM DB store under a temp directory, obtains the stateful service config table, creates an HA manager stub backed by that DB store, and builds the state manager with the Ratis server and transaction buffer. The test saves a `ByteString` configuration under service name `test`, flushes the transaction buffer, and reads the configuration back.

State and persistence behavior: The stateful service configuration is persisted to the temporary DB table only after the HA transaction buffer is flushed. Cleanup closes the DB store.

Dependencies and integration points: This guards persisted service configuration paths used by SCM stateful services and HA replicated transaction buffering.

Risks: Without an explicit flush, buffered writes may not be visible. The broader race around flushing during transaction apply is covered by `TestSCMHATransactionBufferMonitorTask`.

Test signals: The read configuration equals the saved `ByteString` after flush.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestStatefulServiceStateManagerImpl.java -->

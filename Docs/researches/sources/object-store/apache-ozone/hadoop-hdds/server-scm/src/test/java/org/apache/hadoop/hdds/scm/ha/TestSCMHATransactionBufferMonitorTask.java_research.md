<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHATransactionBufferMonitorTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHATransactionBufferMonitorTask.java

Purpose: This suite tests race-sensitive persistence behavior between `SCMHATransactionBufferMonitorTask` and `SCMHADBTransactionBufferImpl`, especially ensuring monitor flushes do not persist buffered data with stale transaction indexes while a Ratis transaction is being applied.

Important APIs and types: It uses real `SCMMetadataStoreImpl`, `SCMHADBTransactionBufferImpl`, `SCMHATransactionBufferMonitorTask`, `Table<String, ByteString>` for stateful service config, `Table<String, TransactionInfo>` for transaction info, `TRANSACTION_INFO_KEY`, mocked `StorageContainerManager`, and an injected `Clock` backed by `AtomicLong`.

Control flow: Setup opens a real SCM metadata store and creates a transaction buffer with a mock clock. Tests first demonstrate the old race when `shouldFlush` and `flush` are called separately and when `flush` is called directly inside an apply window. Then they verify `flushIfNeeded` skips during `beginApplyingTransaction`/`endApplyingTransaction`, including zero-wait calls and a concurrent monitor thread loop, and only flushes after the latest transaction info is updated.

State and persistence behavior: Persistent state is written to temporary SCM DB tables. The tests assert exact on-disk table values for the buffered service config and transaction info. Runtime state includes latest transaction info, apply-in-progress flag, buffer contents, and clock-based flush interval.

Dependencies and integration points: This is a high-value guard for HA state-machine apply, DB transaction buffering, stateful service configuration persistence, and background monitor scheduling.

Risks: Race coverage uses threads and latches; missed synchronization would cause flaky or stale-transaction writes. The test intentionally documents old unsafe behavior as contrast for the guarded API.

Test signals: `statefulServiceConfigTable.get("key")` remains null during apply, later equals `value`, and `transactionInfoTable.get(TRANSACTION_INFO_KEY)` stays at T4 for unsafe paths but reaches T5 for deferred safe paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMHATransactionBufferMonitorTask.java -->

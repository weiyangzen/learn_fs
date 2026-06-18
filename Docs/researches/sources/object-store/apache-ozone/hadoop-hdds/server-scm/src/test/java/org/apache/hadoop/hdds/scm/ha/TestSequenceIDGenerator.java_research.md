<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIDGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIDGenerator.java

Purpose: This suite validates `SequenceIdGenerator` batch allocation, Ratis/non-Ratis behavior, leader failure handling, DB-backed state-manager consistency, restart reinitialization, and invalid sequence type rejection.

Important APIs and types: It uses `SequenceIdGenerator`, `SequenceIdType`, `SequenceIdGenerator.StateManagerImpl`, `SCMMetadataStoreImpl`, `SCMHAManagerStub`, `SCMDBTransactionBufferImpl`, `Table<SequenceIdType, Long>`, `OZONE_SCM_SEQUENCE_ID_BATCH_SIZE`, and `SCMException.ResultCodes.SCM_NOT_LEADER`.

Control flow: Non-Ratis and Ratis tests create real SCM metadata stores and assert IDs advance through initial and invalidated batches, using default batch size 1000 or configured batch size 100. The not-leader test spies the state manager, lets the first batch allocate, then makes later batch allocation throw `SCM_NOT_LEADER` and verifies generated IDs never exceed the current batch. Additional tests exercise direct state-manager allocation from empty DB, expected-last-ID mismatch failure, reinitialization from a pre-populated sequence ID table, and rejection of an unknown sequence ID name.

State and persistence behavior: Temporary SCM metadata DB tables persist last allocated IDs. Runtime state includes per-type in-memory last-ID map, current batch range, invalidation, and DB transaction buffer behavior.

Dependencies and integration points: This protects SCM ID allocation for local IDs, delete transaction IDs, container IDs, and HA replicated batch reservations.

Risks: Batch allocation must be monotonic and leader-gated. A stale in-memory map or DB mismatch can cause duplicate IDs after restart or across SCMs.

Test signals: Exact generated ID sequences, no ID beyond current batch after simulated not-leader failure, state-manager `getLastId` values, true/false allocation outcomes, successful reinitialize from DB, and exception path for unknown sequence type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSequenceIDGenerator.java -->

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestReconInternalSchemaDefinition.java

Purpose: This test validates the internal Recon task-status schema and generated DAO CRUD behavior for `RECON_TASK_STATUS`. It ensures the schema has the expected columns/types and that task status records can be created, read, updated, and deleted.

Important APIs/types/functions: The class extends `AbstractReconSqlDBTest` and uses `RECON_TASK_STATUS_TABLE_NAME`, JDBC `Connection`, `DatabaseMetaData`, `ResultSet`, SQL `Types`, `ReconTaskStatusDao`, and `ReconTaskStatus` POJO.

Control flow: `testSchemaCreated` reads database metadata for the task status table columns, builds actual `(name,type)` pairs, and compares them to the expected ordered list. `testReconTaskStatusCRUDOperations` verifies table presence, inserts two records, reads one by id, updates its sequence number, deletes the other, and verifies deletion.

State and persistence behavior: State is persisted in the per-test Derby Recon SQL DB created by the base class. The table stores task name, last updated timestamp, last updated sequence number, last task run status, and current-running flag.

Dependencies and integration points: This schema supports Recon background task bookkeeping and task status updater behavior. The test integrates generated jOOQ DAO classes with the schema produced by `ReconSchemaManager`.

Risks: Column order is asserted exactly, which is useful for compatibility but can be brittle if metadata ordering differs by DB dialect. The CRUD test leaves one updated record in the per-test DB, relying on temp DB isolation. It does not assert default values for status/running fields when omitted.

Test signals: Exactly five columns with expected SQL types; table metadata exists; inserted `HelloWorldTask` has timestamp and sequence 100; update changes sequence to 150; deleting `GoodbyeWorldTask` makes `findById` return null.

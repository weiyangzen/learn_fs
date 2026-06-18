# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestStatsSchemaDefinition.java

Purpose: This test validates the global stats schema and generated DAO CRUD behavior. It ensures `GLOBAL_STATS` has the expected columns and that `GlobalStatsDao` can insert, read, update, and delete statistic records with timestamps.

Important APIs/types/functions: The class extends `AbstractReconSqlDBTest` and uses `GLOBAL_STATS_TABLE_NAME`, JDBC `Connection`, `DatabaseMetaData`, `ResultSet`, SQL `Types`, `GlobalStatsDao`, `GlobalStats`, and `Timestamp`.

Control flow: `testIfStatsSchemaCreated` fetches metadata columns for the global stats table and compares ordered `(name,type)` pairs against `key`, `value`, and `last_updated_timestamp`. `testGlobalStatsCRUDOperations` verifies table presence, inserts two records, reads each by key, updates `key2` value and timestamp, then deletes `key1` and verifies it is gone.

State and persistence behavior: Persistent state is the per-test Derby Recon SQL DB. The global stats table stores stat key, long value, and last-updated timestamp. DAO operations mutate this table directly.

Dependencies and integration points: Global stats support Recon-wide counters and summaries. The test integrates `StatsSchemaDefinition` output from schema generation with jOOQ-generated `GlobalStatsDao` and POJO mappings.

Risks: Like other schema metadata tests, exact column ordering can be dialect-sensitive. Timestamp equality depends on Java/JDBC preserving millisecond precision for Derby in this setup. The test covers two records but not duplicate-key behavior or null constraints.

Test signals: Exactly three columns with expected SQL types; inserted `key1` has value 500 and exact timestamp; inserted `key2` has value 10 and timestamp plus one second; update changes `key2` to value 100 and later timestamp; deleting `key1` makes DAO lookup return null.

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestSchemaVersionTableDefinition.java

Purpose: This suite verifies the Recon schema-version table definition and upgrade initialization semantics. It tests table columns, basic CRUD, fresh-install behavior, pre-upgrade cluster behavior where other tables exist but schema version does not, and upgraded-cluster behavior where an existing metadata layout version must be preserved.

Important APIs/types/functions: It extends `AbstractReconSqlDBTest` and uses `SCHEMA_VERSION_TABLE_NAME`, `SchemaVersionTableDefinition`, `ReconSchemaVersionTableManager`, `ReconLayoutVersionManager`, `ReconContext`, `GLOBAL_STATS_TABLE_NAME`, `UNHEALTHY_CONTAINERS_TABLE_NAME`, `SqlDbUtils.TABLE_EXISTS_CHECK`, `listAllTables`, jOOQ `DSLContext`, `SQLDataType`, `Timestamp`, JDBC metadata, and mocked `DataSource`.

Control flow: `testSchemaVersionTableCreation` checks metadata for `version_number` and `applied_on`. `testSchemaVersionCRUDOperations` drops all tables, creates only schema version table, inserts version 1, updates to 2, and deletes. Fresh install drops all tables, initializes schema with latest SLV 3, and expects layout manager current MLV 3. Pre-upgrade drops only schema version and ensures other tables exist, initializes, then expects current MLV -1. Upgraded-cluster creates other tables plus schema version, inserts MLV 2, initializes with latest SLV 3, and expects MLV remains 2.

State and persistence behavior: Persistent state is the per-test Derby DB. Tests intentionally drop and create tables to simulate installation and upgrade scenarios. Schema version rows store `version_number` and `applied_on`; the layout version manager reads current MLV from this table.

Dependencies and integration points: This is a key upgrade safety test connecting schema initialization with Recon's layout-version manager. It integrates table-existence checks, all-table listing, manual jOOQ DDL, schema-version manager, and upgrade-state inference from existing database tables.

Risks: Helper-created mock tables only have `id` and `data` columns, so they simulate presence rather than real schema. `assertEquals(true, tableExists)` is less idiomatic but clear. Dropping all tables inside a test relies on isolated DBs from the base class. The latest SLV value 3 is hard-coded in tests and must track production layout changes.

Test signals: Schema version table has exactly two columns with integer and timestamp types; CRUD changes version 1 to 2 and then leaves zero rows; fresh install creates table and sets MLV to 3; pre-upgraded cluster creates table and reports MLV -1; upgraded cluster preserves stored MLV 2 despite latest SLV 3.

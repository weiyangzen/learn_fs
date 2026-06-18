# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SchemaVersionTableDefinition.java

## Purpose
`SchemaVersionTableDefinition` is the Recon SQL codegen-side schema definition for the `RECON_SCHEMA_VERSION` table. It ensures Recon has a table that records the active schema/software layout version and bootstraps that value on fresh installations.

## Important APIs, Types, And Functions
The class implements `ReconSchemaDefinition`, is Guice `@Singleton`, and exposes `SCHEMA_VERSION_TABLE_NAME`, `initializeSchema()`, and `setLatestSLV(int)`. Private helpers `createSchemaVersionTable(DSLContext)` and `insertInitialSLV(DSLContext,int)` perform jOOQ DDL and initial insert.

## Control Flow
`initializeSchema()` opens a JDBC connection, builds a local `DSLContext`, checks table existence with `SqlDbUtils.TABLE_EXISTS_CHECK`, detects fresh installs by calling `listAllTables(conn)`, creates the table if missing, and inserts `latestSLV` only when no other tables existed.

## State And Persistence
Persistent state is a SQL table with `version_number` and timestamp `applied_on`. Runtime state is the injected `DataSource` and mutable `latestSLV`, which must be set by `ReconSchemaManager` before initialization.

## Dependencies And Integration Points
It depends on `DataSource`, JDBC, jOOQ DSL/data types, and `SqlDbUtils`. `ReconSchemaManager` initializes it before other schema definitions and passes the latest value derived from `ReconLayoutFeature`.

## Risks
If `setLatestSLV` is not called before a fresh install, version `0` can be inserted. Table existence is probed by selecting from the table name, so dialect-specific quoting or permission failures look like absence. Existing installs with other tables but no version row create an empty version table and rely on later migration code.

## Test Signals
Useful tests verify fresh install insert behavior, non-fresh empty-version behavior, table DDL shape, timestamp defaulting, and idempotent second initialization.

# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaVersionTableManager.java

## Purpose
`ReconSchemaVersionTableManager` reads and updates the single-row `RECON_SCHEMA_VERSION` table used by Recon layout upgrade finalization.

## Important APIs, Types, And Functions
The constructor injects a `DataSource` and initializes a jOOQ `DSLContext`. `getCurrentSchemaVersion()` fetches `version_number`, returning `-1` when no row exists. `updateSchemaVersion(int, Connection)` updates an existing row or inserts a new row. `getDataSource()` exposes the datasource.

## Control Flow
Upgrade code reads the current version through `getCurrentSchemaVersion()`. After a feature finalizes, it passes the migration connection to `updateSchemaVersion`, which switches the DSL context to that connection, checks for any row, and writes the version and current timestamp.

## State And Persistence
Persistent state is the version row and `applied_on` timestamp. Runtime state is a mutable `DSLContext` plus the injected datasource; the constructor obtains a connection without closing it.

## Dependencies And Integration Points
It depends on JDBC, jOOQ, and `ReconLayoutVersionManager`, which drives finalization after `ReconServer` starts services.

## Risks
The constructor connection may leak. The table is assumed to contain at most one row, but no primary key or uniqueness is enforced by this manager. `getCurrentSchemaVersion()` Javadoc says 0 for empty/missing table but implementation returns `-1` for empty and throws for missing/inaccessible table.

## Test Signals
Tests should cover empty table, missing table, update-vs-insert, timestamp changes, multi-row behavior, and exception wrapping.

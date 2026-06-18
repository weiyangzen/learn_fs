# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/SqlDbUtils.java

## Purpose
`SqlDbUtils` centralizes SQL helper constants and utility functions used by Recon schema bootstrap and code generation. It abstracts Derby creation/log suppression and a shared table-existence probe.

## Important APIs, Types, And Functions
Key constants are `DERBY_DRIVER_CLASS`, `SQLITE_DRIVER_CLASS`, and `DERBY_DISABLE_LOG_METHOD`. `TABLE_EXISTS_CHECK` is a `BiPredicate<Connection,String>` using jOOQ `select(count()).from(tableName)`. Other APIs are `createNewDerbyDatabase`, `disableDerbyLogFile`, and `listAllTables`.

## Control Flow
`createNewDerbyDatabase` sets Derby's error method, loads the embedded driver, then opens a `create=true` connection with the supplied schema name. `TABLE_EXISTS_CHECK` executes a count query and returns false on `DataAccessException`. `listAllTables` iterates JDBC metadata table rows.

## State And Persistence
The class is static and final. Persistent effects are Derby database creation and system property mutation for embedded Derby logging. `listAllTables` only reads metadata.

## Dependencies And Integration Points
It depends on JDBC, jOOQ, Derby/SQLite driver class names, SLF4J, and Java `OutputStream`. Schema definitions call the table check before creating Recon SQL tables; `SchemaVersionTableDefinition` uses `listAllTables` to identify fresh installs.

## Risks
The existence check treats any jOOQ data access failure as "table missing", which can hide permission, syntax, or connection errors. `listAllTables` does not filter system schemas, so its fresh-install semantics depend on the JDBC driver's metadata behavior. Derby logging suppression changes a JVM-wide property.

## Test Signals
Tests should cover Derby URL creation, no-op log stream behavior, table-exists true and false paths, metadata table listing, and failure behavior for invalid connections.

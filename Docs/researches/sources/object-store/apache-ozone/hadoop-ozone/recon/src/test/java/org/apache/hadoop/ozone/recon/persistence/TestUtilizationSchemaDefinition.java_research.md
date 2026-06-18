# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/persistence/TestUtilizationSchemaDefinition.java

## Purpose
End-to-end SQL schema and DAO test for Recon utilization tables. It verifies generated Derby schema metadata and CRUD behavior for cluster growth and file-count-by-size persistence.

## Important APIs, types, and functions
- Extends `AbstractReconSqlDBTest` for a real Recon SQL test database, jOOQ `DSLContext`, and DAO lookup helpers.
- Uses `UtilizationSchemaDefinition` table constants for `CLUSTER_GROWTH_DAILY`, `FILE_COUNT_BY_SIZE`, and `CONTAINER_COUNT_BY_SIZE`.
- Uses JDBC `DatabaseMetaData` to inspect columns and jOOQ-generated DAOs/POJOs such as `ClusterGrowthDailyDao`, `FileCountBySizeDao`, `ClusterGrowthDaily`, and `FileCountBySize`.

## Control flow
`testReconSchemaCreated` queries column metadata for all utilization tables and compares column names and JDBC types in expected order. `testClusterGrowthDailyCRUDOperations` confirms the table exists, inserts one composite-key record, reads it through a jOOQ record key, updates two fields, re-reads, deletes by composite key, and checks the row is gone. `testFileCountBySizeCRUDOperations` inserts a volume/bucket/file-size count row, reads it by the three-part key, updates the count, and inspects the table keys.

## State and persistence behavior
The tested state is relational schema shape and jOOQ DAO persistence. `CLUSTER_GROWTH_DAILY` is keyed by timestamp and datanode id. `FILE_COUNT_BY_SIZE` is keyed by volume, bucket, and file size. The test makes sure updates overwrite rows in place and deletes clear the composite-key lookup.

## Dependencies and integration points
This file sits between Recon schema definitions, generated jOOQ classes, Derby metadata, and utilization APIs that depend on daily growth and histogram tables. It is a schema compatibility guard for generated DAO code.

## Risks and edge cases
Assertions depend on exact column order returned by Derby metadata and exact JDBC type constants. The file-count test does not assert unique key names, only that keys are accessible. It does not cover container-count CRUD beyond schema shape.

## Test signals
Signals are exact column lists, successful insert/read/update/delete cycles, null after deletion, and correct count update behavior through generated DAOs.

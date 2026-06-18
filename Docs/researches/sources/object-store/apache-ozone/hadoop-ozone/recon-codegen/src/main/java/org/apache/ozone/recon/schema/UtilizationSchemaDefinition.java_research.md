# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/UtilizationSchemaDefinition.java

## Purpose
`UtilizationSchemaDefinition` defines SQL tables used for historical utilization and size-distribution reporting in Recon.

## Important APIs, Types, And Functions
The public table names are `CLUSTER_GROWTH_DAILY`, `FILE_COUNT_BY_SIZE`, and `CONTAINER_COUNT_BY_SIZE`. `initializeSchema()` creates all three when missing. `getDSLContext()` exposes the last initialized jOOQ context for tests or codegen support.

## Control Flow
Initialization opens a connection, assigns `dslContext`, checks each table with `TABLE_EXISTS_CHECK`, and invokes `createFileSizeCountTable`, `createClusterGrowthTable`, or `createContainerSizeCountTable` as needed. The method is annotated `@Transactional`, but the actual transaction boundary depends on the surrounding injector/persistence setup.

## State And Persistence
Persistent tables track daily datanode growth samples, file-size counts per volume/bucket/bin, and container-size bin counts. Runtime state is limited to `DataSource` and the mutable `DSLContext`.

## Dependencies And Integration Points
It uses Guice, Spring transaction annotations, JDBC, jOOQ, and generated DAO consumers such as `ClusterGrowthDailyDao`, `FileCountBySizeDao`, and `ContainerCountBySizeDao`.

## Risks
Connections are not closed directly. Table primary-key names are global strings and may collide in dialects that do not scope constraint names by table. Size-bin writers must match the primary-key dimensions exactly or updates become duplicate inserts.

## Test Signals
Tests should assert table creation, idempotency, primary keys, DAO compatibility, and population/readback from utilization tasks and endpoints.

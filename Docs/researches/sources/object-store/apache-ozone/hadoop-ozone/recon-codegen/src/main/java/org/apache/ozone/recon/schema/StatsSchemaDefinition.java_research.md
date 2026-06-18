# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/StatsSchemaDefinition.java

## Purpose
`StatsSchemaDefinition` creates Recon's `GLOBAL_STATS` SQL table, which stores keyed cluster and OM table count values used by summary APIs.

## Important APIs, Types, And Functions
The class implements `ReconSchemaDefinition`, declares `GLOBAL_STATS_TABLE_NAME`, and exposes `initializeSchema()`. Private `createGlobalStatsTable()` creates columns `key`, `value`, and `last_updated_timestamp` with primary key `pk_key`.

## Control Flow
Initialization gets a connection from the injected `DataSource`, creates a jOOQ `DSLContext`, probes for `GLOBAL_STATS`, and calls the DDL helper only when the table is absent.

## State And Persistence
Persistent state is the `GLOBAL_STATS` table keyed by a varchar stat name. Runtime state includes a mutable `DSLContext` field and the injected `DataSource`; the connection opened in `initializeSchema()` is not closed in this implementation.

## Dependencies And Integration Points
It depends on Guice, JDBC, jOOQ, and `SqlDbUtils.TABLE_EXISTS_CHECK`. Runtime code such as `ReconUtils.upsertGlobalStatsTable`, `ReconGlobalStatsManager`, `OmTableInsightTask`, and `ClusterStateEndpoint` relies on these rows.

## Risks
The unclosed connection is a resource-leak risk during repeated test or bootstrap runs. The table uses a generic `key` column, which can be dialect-sensitive. Failures in table-existence probing can lead to redundant DDL attempts.

## Test Signals
Tests should verify DDL shape, idempotent initialization, primary-key enforcement, insert/update compatibility through generated DAO classes, and connection cleanup under failures.

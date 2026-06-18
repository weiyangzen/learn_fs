# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconSchemaManager.java

## Purpose
`ReconSchemaManager` orchestrates creation of all Recon SQL schema definitions during server startup.

## Important APIs, Types, And Functions
The constructor receives a Guice set of `ReconSchemaDefinition`. `createReconSchema()` initializes the schema version table first, then all other definitions. `calculateLatestSLV()` delegates to `ReconLayoutFeature.determineSLV()`.

## Control Flow
Startup calls `createReconSchema()`. It computes the latest software layout version, finds `SchemaVersionTableDefinition`, sets its latest SLV, initializes it, then iterates non-version definitions and calls `initializeSchema()` on each while logging `SQLException`s.

## State And Persistence
The manager stores a set of schema definitions. Persistent effects are whatever DDL each definition performs against the SQL datasource.

## Dependencies And Integration Points
It depends on generated schema definitions from `ReconSchemaGenerationModule`, `SchemaVersionTableDefinition`, `ReconLayoutFeature`, and SLF4J. `ReconServer` invokes it before service startup and layout upgrade finalization.

## Risks
Initialization errors are logged but not rethrown, so the server may continue with incomplete schema and fail later. HashSet iteration gives no ordering among non-version tables. Missing version definition silently skips version-table creation.

## Test Signals
Tests should verify version table first, latest SLV injection, all definitions invoked, exception handling, and behavior with absent or failing definitions.

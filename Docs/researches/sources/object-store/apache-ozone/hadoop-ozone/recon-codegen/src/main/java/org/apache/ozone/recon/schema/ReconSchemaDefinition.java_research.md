<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaDefinition.java

## Purpose
Common interface for Recon schema providers used by code generation and schema initialization.

## Important APIs, types, and functions
Declares one method, `initializeSchema()`, which executes DDL and may throw `SQLException`.

## Control flow
Implementations are invoked by `JooqCodeGenerator.initializeSchema` after Guice multibinding discovery.

## State and persistence behavior
The interface has no state. Implementations persist tables, indexes, and constraints.

## Dependencies and integration points
Implemented by container, task, utilization, stats, and schema-version definitions. New schema definitions must also be bound in `ReconSchemaGenerationModule`.

## Risks and test signals
The interface is intentionally minimal; it does not model migrations, ordering, or idempotency beyond each implementation. Tests should ensure every bound definition can run repeatedly against an existing schema.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaDefinition.java -->

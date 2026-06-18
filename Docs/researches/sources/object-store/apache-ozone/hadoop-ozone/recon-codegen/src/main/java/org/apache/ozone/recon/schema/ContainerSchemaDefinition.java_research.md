<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ContainerSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ContainerSchemaDefinition.java

## Purpose
Programmatic Recon schema definition for unhealthy container tracking.

## Important APIs, types, and functions
Implements `ReconSchemaDefinition` as a Guice singleton. Defines `UNHEALTHY_CONTAINERS`, columns for container ID/state/timestamps/replica counts/delta/reason, primary key on `(container_id, container_state)`, check constraint over `UnHealthyContainerStates`, and composite index `idx_state_container_id`.

## Control flow
`initializeSchema` opens a datasource connection, creates a jOOQ DSL context, checks table existence through `SqlDbUtils.TABLE_EXISTS_CHECK`, and creates the table/index if missing.

## State and persistence behavior
Persists Derby/SQL table and index DDL in the target Recon schema. The class retains the datasource and last DSL context.

## Dependencies and integration points
Bound into `ReconSchemaGenerationModule` and used by `JooqCodeGenerator`. Runtime Recon code relies on the generated jOOQ artifacts and table layout for unhealthy container queries and pagination.

## Risks and test signals
The check constraint must stay aligned with enum values used by Recon. Existing databases will not be migrated by this create-if-missing path. The composite index encodes important pagination performance assumptions. Tests should verify DDL, constraints, generated classes, and query plans for state-filtered pagination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ContainerSchemaDefinition.java -->

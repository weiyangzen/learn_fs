<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconTaskSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconTaskSchemaDefinition.java

## Purpose
Programmatic Recon schema definition for tracking Recon task execution state.

## Important APIs, types, and functions
Implements `ReconSchemaDefinition` as a Guice singleton. Defines `RECON_TASK_STATUS` with columns `task_name`, `last_updated_timestamp`, `last_updated_seq_number`, `last_task_run_status`, and `is_current_task_running`, with primary key `task_name`.

## Control flow
`initializeSchema` obtains a connection, checks for the table, and calls `createReconTaskStatusTable` when absent. DDL is built with jOOQ `DSL.using(conn).createTableIfNotExists`.

## State and persistence behavior
Persists the task status table in the Recon SQL schema. The class holds only the datasource reference.

## Dependencies and integration points
Bound in `ReconSchemaGenerationModule` and consumed by `JooqCodeGenerator`. Runtime Recon task management depends on the generated DAO/POJO for this table.

## Risks and test signals
There is no migration path for existing tables with older columns. Integer status/running fields require consistent interpretation by task code. Tests should validate idempotent initialization, generated classes, primary key constraint, and runtime task status reads/writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconTaskSchemaDefinition.java -->
